"""
Script para inicializar o Vector Store
Execute este script uma vez para criar o banco de dados vetorial
"""
import os
import sys
import logging

sys.path.append(os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from vector_store import VectorStoreManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing Vector Store")
    logger.info("This process will load products, generate embeddings, and create the vector database")
    logger.info("Estimated time: 5-10 minutes")
    
    try:
        vector_store = VectorStoreManager()
        logger.info("Vector Store initialized successfully")
        logger.info("Semantic search is now available")
        
    except Exception as e:
        logger.error(f"Failed to initialize Vector Store: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
