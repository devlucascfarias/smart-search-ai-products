"""
Vector Store Manager for Smart Search AI
Manages embeddings and semantic search of products using Chroma DB
"""
import os
import pandas as pd
import logging
from typing import List, Dict, Optional
from pathlib import Path

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from products import get_df_by_category, ALL_CATEGORIES, translate_category

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages the vector store of products for semantic search"""
    
    def __init__(self, persist_directory: str = None):
        if persist_directory is None:
            persist_directory = os.path.join(os.path.dirname(__file__), "chroma_db")
        
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        
        self.vector_store = None
        self._load_or_create_store()
    
    def _load_or_create_store(self):
        """Loads existing vector store or creates a new one"""
        try:
            self.vector_store = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings,
                collection_name="products"
            )
            
            if self.vector_store._collection.count() > 0:
                logger.info(f"Vector store loaded with {self.vector_store._collection.count()} products")
                return
        except Exception as e:
            logger.warning(f"Could not load existing vector store: {e}")
        
        logger.info("Creating new vector store")
        self._create_new_store()
    
    def _create_new_store(self):
        """Creates a new vector store with all products"""
        import time
        
        documents = []
        
        logger.info(f"Processing {len(ALL_CATEGORIES)} categories")
        
        for i, category in enumerate(ALL_CATEGORIES, 1):
            try:
                df = get_df_by_category(category)
                if df is None or len(df) == 0:
                    continue
                
                category_translated = translate_category(category)
                df_sample = df.head(50)
                
                for _, row in df_sample.iterrows():
                    product_text = f"{row['name']} - Category: {category_translated}"
                    
                    doc = Document(
                        page_content=product_text,
                        metadata={
                            "name": row['name'],
                            "category": category,
                            "category_translated": category_translated,
                            "sub_category": row.get('sub_category', ''),
                            "image": row.get('image', ''),
                            "link": row.get('link', ''),
                            "ratings": float(row.get('ratings', 0)) if pd.notna(row.get('ratings')) else 0,
                            "actual_price": str(row.get('actual_price', '0'))
                        }
                    )
                    documents.append(doc)
                
                if i % 20 == 0:
                    logger.info(f"Processed {i}/{len(ALL_CATEGORIES)} categories")
                
            except Exception as e:
                logger.error(f"Error processing category {category}: {e}")
                continue
        
        logger.info(f"Total documents: {len(documents)}")
        logger.info("Generating embeddings in batches (respecting rate limits)")
        
        batch_size = 500
        total_batches = (len(documents) + batch_size - 1) // batch_size
        
        self.vector_store = Chroma(
            persist_directory=str(self.persist_directory),
            embedding_function=self.embeddings,
            collection_name="products"
        )
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min((batch_num + 1) * batch_size, len(documents))
            batch_docs = documents[start_idx:end_idx]
            
            logger.info(f"Processing batch {batch_num + 1}/{total_batches} ({len(batch_docs)} documents)")
            
            try:
                self.vector_store.add_documents(batch_docs)
                logger.info(f"Batch {batch_num + 1} completed successfully")
                
                if batch_num < total_batches - 1:
                    delay = 20
                    logger.info(f"Waiting {delay}s before next batch")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error in batch {batch_num + 1}: {e}")
                if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                    logger.warning("Rate limit reached, waiting 60s before retry")
                    time.sleep(60)
                    try:
                        self.vector_store.add_documents(batch_docs)
                        logger.info(f"Batch {batch_num + 1} completed after retry")
                    except Exception as retry_error:
                        logger.error(f"Retry failed: {retry_error}")
                        continue
        
        logger.info("Vector store created successfully")
    
    def search_products(
        self, 
        query: str, 
        category: Optional[str] = None,
        k: int = 20
    ) -> List[Dict]:
        """
        Search products using semantic similarity
        
        Args:
            query: User search text
            category: Category to filter (optional)
            k: Number of results
            
        Returns:
            List of relevant products
        """
        if self.vector_store is None:
            return []
        
        filter_dict = None
        if category:
            filter_dict = {"category": category}
        
        results = self.vector_store.similarity_search(
            query,
            k=k,
            filter=filter_dict
        )
        
        products = []
        for doc in results:
            products.append({
                "name": doc.metadata.get("name", ""),
                "category": doc.metadata.get("category", ""),
                "category_translated": doc.metadata.get("category_translated", ""),
                "sub_category": doc.metadata.get("sub_category", ""),
                "image": doc.metadata.get("image", ""),
                "link": doc.metadata.get("link", ""),
                "ratings": doc.metadata.get("ratings", 0),
                "actual_price": doc.metadata.get("actual_price", "0"),
                "relevance_score": getattr(doc, 'score', 1.0)
            })
        
        return products
    
    def rebuild_store(self):
        """Rebuilds the vector store from scratch"""
        logger.info("Rebuilding vector store")
        
        if self.persist_directory.exists():
            import shutil
            shutil.rmtree(self.persist_directory)
            self.persist_directory.mkdir(exist_ok=True)
        
        self._create_new_store()

vector_store_manager = None

def get_vector_store() -> VectorStoreManager:
    """Returns the global vector store instance (lazy loading)"""
    global vector_store_manager
    if vector_store_manager is None:
        vector_store_manager = VectorStoreManager()
    return vector_store_manager
