import os
import pandas as pd
from dotenv import load_dotenv
from typing import List, Dict, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

import sys
sys.path.append(os.path.dirname(__file__))
from products import get_df_by_category, ALL_CATEGORIES, Product, get_products_summary, get_categories_with_names
from prompt_manager import prompt_manager
from vector_store import get_vector_store

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.4
)

app = FastAPI(
    title="Smart Search Products (LangChain)",
    description="Assistente de compras inteligente com busca semântica."
)

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Smart Search Products Backend is running"}

@app.post("/vector-store/rebuild")
async def rebuild_vector_store():
    """Reconstrói o vector store do zero (use apenas quando necessário)"""
    try:
        vector_store = get_vector_store()
        vector_store.rebuild_store()
        return {"status": "success", "message": "Vector store reconstruído com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vector-store/search")
async def semantic_search(query: str, category: Optional[str] = None, limit: int = 20):
    """Busca semântica direta no vector store"""
    try:
        vector_store = get_vector_store()
        results = vector_store.search_products(query, category=category, k=limit)
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisResult(BaseModel):
    budget: Optional[float] = None
    categories: List[str]

class PromptRequest(BaseModel):
    prompt: str
    budget: Optional[float] = None

@app.post("/generate")
async def generate_text(request: PromptRequest):
    try:
        """ Análise de Intenção """
        parser = JsonOutputParser(pydantic_object=AnalysisResult)
        
        # Carrega prompt de análise de categoria de arquivo externo
        analysis_template = prompt_manager.load_prompt("category_analysis")
        
        analysis_prompt = PromptTemplate(
            template=analysis_template,
            input_variables=["query", "available_categories"]
        )

        analysis_chain = analysis_prompt | llm | parser
        
        analysis_data = analysis_chain.invoke({
            "query": request.prompt,
            "available_categories": get_categories_with_names()
        })
        
        max_price = request.budget or analysis_data.get("budget")
        relevant_categories = [cat for cat in analysis_data.get("categories", []) if cat in ALL_CATEGORIES]

        """ Busca de Dados Reais """
        context_data = ""
        if relevant_categories:
            for cat in relevant_categories[:5]: 
                summary = get_products_summary(cat, limit=18, max_price=max_price, search_query=request.prompt)
                if summary and "NADA_ENCONTRADO" not in summary:
                    context_data += summary + "\n"
        
        # Se não encontrou nada, retorna mensagem amigável
        if not context_data or context_data.strip() == "":
            return {
                "response": f"Desculpe, não encontramos produtos disponíveis para **{request.prompt}** no momento. Tente refinar sua busca ou explorar nossas categorias.",
                "detected_budget": max_price,
                "queried_categories": relevant_categories
            }
        
        """ Geração da Resposta Final """
        budget_info = f" (com orçamento de até R$ {max_price})" if max_price else ""
        
        from products import translate_category
        relevant_cat_translated = translate_category(relevant_categories[0]) if relevant_categories else "nossas categorias"

        # Carrega prompt de geração de resposta de arquivo externo
        response_template = prompt_manager.load_prompt("response_generation")
        
        final_prompt = PromptTemplate(
            template=response_template,
            input_variables=["query", "context", "budget_info", "relevant_category_name"]
        )

        final_chain = final_prompt | llm
        
        response = final_chain.invoke({
            "query": request.prompt,
            "context": context_data if context_data else "NADA_ENCONTRADO",
            "budget_info": budget_info,
            "relevant_category_name": relevant_cat_translated
        })

        return {
            "response": response.content,
            "detected_budget": max_price,
            "queried_categories": relevant_categories
        }
    
    except Exception as e:
        print(f"Erro LangChain: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
async def get_categories():
    
    from products import translate_category
    return [{"id": cat, "name": translate_category(cat)} for cat in ALL_CATEGORIES]

@app.get("/products/{category}")
async def get_products_by_category(category: str, page: int = 1, page_size: int = 20):
    df = get_df_by_category(category)
    if df is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    total_products = len(df)
    total_pages = (total_products + page_size - 1) // page_size
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    df_slice = df.iloc[start_idx:end_idx].copy()
    
    from products import clean_price, INR_TO_BRL
    
    products_list = []
    for _, row in df_slice.iterrows():
        p = row.fillna("").to_dict()
        price_inr = clean_price(p.get('actual_price', '0'))
        p['actual_price'] = f"R$ {price_inr * INR_TO_BRL:.2f}"
        products_list.append(p)
        
    return {
        "products": products_list,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "total_products": total_products
    }