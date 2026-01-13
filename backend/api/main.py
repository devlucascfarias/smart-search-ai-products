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
    description="Intelligent shopping assistant with semantic search."
)

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Smart Search Products Backend is running"}

@app.post("/vector-store/rebuild")
async def rebuild_vector_store():
    """Rebuilds the vector store from scratch (use only when necessary)"""
    try:
        vector_store = get_vector_store()
        vector_store.rebuild_store()
        return {"status": "success", "message": "Vector store rebuilt successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vector-store/search")
async def semantic_search(query: str, category: Optional[str] = None, limit: int = 20):
    """Direct semantic search in the vector store"""
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
        parser = JsonOutputParser(pydantic_object=AnalysisResult)
        
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

        context_data = ""
        if relevant_categories:
            for cat in relevant_categories[:5]: 
                summary = get_products_summary(cat, limit=18, max_price=max_price, search_query=request.prompt)
                if summary and "NOT_FOUND" not in summary:
                    context_data += summary + "\n"
        
        if not context_data or context_data.strip() == "":
            return {
                "response": f"Sorry, we couldn't find available products for **{request.prompt}** at the moment. Try refining your search or explore our categories.",
                "detected_budget": max_price,
                "queried_categories": relevant_categories
            }
        
        budget_info = f" (with budget up to {max_price})" if max_price else ""
        
        relevant_cat_name = relevant_categories[0] if relevant_categories else "our categories"

        response_template = prompt_manager.load_prompt("response_generation")
        
        final_prompt = PromptTemplate(
            template=response_template,
            input_variables=["query", "context", "budget_info", "relevant_category_name"]
        )

        final_chain = final_prompt | llm
        
        response = final_chain.invoke({
            "query": request.prompt,
            "context": context_data if context_data else "NOT_FOUND",
            "budget_info": budget_info,
            "relevant_category_name": relevant_cat_name
        })

        return {
            "response": response.content,
            "detected_budget": max_price,
            "queried_categories": relevant_categories
        }
    
    except Exception as e:
        print(f"LangChain Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
async def get_categories():
    
    return [{"id": cat, "name": cat} for cat in ALL_CATEGORIES]

@app.get("/products/{category}")
async def get_products_by_category(category: str, page: int = 1, page_size: int = 20):
    df = get_df_by_category(category)
    if df is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    total_products = len(df)
    total_pages = (total_products + page_size - 1) // page_size
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    df_slice = df.iloc[start_idx:end_idx].copy()
    
    from products import clean_price
    
    products_list = []
    for _, row in df_slice.iterrows():
        p = row.fillna("").to_dict()
        products_list.append(p)
        
    return {
        "products": products_list,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "total_products": total_products
    }