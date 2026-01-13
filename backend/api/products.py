import os
import pandas as pd
from typing import List, Dict, Optional
from pydantic import BaseModel

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

# Original prices are in INR (₹)

_LOADED_PRODUCTS: Dict[str, pd.DataFrame] = {}

def get_available_categories() -> List[str]:
    """Returns only the list of categories that have data (files > 100 bytes)."""
    if not os.path.exists(DATA_DIR):
        return []
    
    categories = []
    for f in os.listdir(DATA_DIR):
        if f.endswith(".csv"):
            file_path = os.path.join(DATA_DIR, f)
            if os.path.getsize(file_path) > 100:
                categories.append(f.replace(".csv", ""))
    return categories

def get_df_by_category(category: str) -> Optional[pd.DataFrame]:
    """Loads the DataFrame of a specific category on demand."""
    if category in _LOADED_PRODUCTS:
        return _LOADED_PRODUCTS[category]
    
    file_path = os.path.join(DATA_DIR, f"{category}.csv")
    if os.path.exists(file_path):
        try:
            if os.path.getsize(file_path) > 100:
                df = pd.read_csv(file_path)
                if len(_LOADED_PRODUCTS) > 5:
                    _LOADED_PRODUCTS.clear()
                
                _LOADED_PRODUCTS[category] = df
                return df
            else:
                # Returns an empty DataFrame with correct columns if file is small
                return pd.DataFrame(columns=['name','main_category','sub_category','image','link','ratings','no_of_ratings','discount_price','actual_price'])
        except Exception as e:
            print(f"Error loading {category}: {e}")
    return None

def get_categories_with_names() -> str:
    """Returns a formatted string 'ID: Name' for the AI prompt."""
    return "\n".join([f"- {cat}" for cat in ALL_CATEGORIES])

ALL_CATEGORIES = get_available_categories()

class Categories(BaseModel):
    all_categories: List[str]
    product_category: str

class Product(BaseModel):
    name: str
    main_category: str
    sub_category: str
    image: str
    link: str
    ratings: float = None
    no_of_ratings: str = None
    discount_price: str = None
    actual_price: str = None

def clean_price(price_str: str) -> float:
    try:
        if not price_str or pd.isna(price_str):
            return 0.0
        cleaned = "".join(c for c in str(price_str) if c.isdigit() or c in ".,")
        cleaned = cleaned.replace(",", "")
        return float(cleaned)
    except:
        return 0.0

def get_products_summary(category: str, limit: int = 18, max_price: float = None, search_query: str = None) -> str:
    df = get_df_by_category(category)
    if df is None:
        return f"Category '{category}' not found or error loading."
    
    filtered_df = df.copy()
    
    # 1. Price Filter
    if max_price:
        filtered_df = filtered_df[filtered_df['actual_price'].apply(clean_price) <= max_price]

    if filtered_df.empty:
        return "NADA_ENCONTRADO"
    
    products = filtered_df.head(30)
    
    summary = f"Real Products Available in category '{category}':\n"
    for _, row in products.iterrows():
        price = row.get('actual_price', '0')
        # Using clear labels and avoiding pipes which cause extraction issues in the LLM
        summary += f"- PRODUCT_NAME: {row['name']} PRODUCT_PRICE: {price} PRODUCT_RATING: {row.get('ratings', 'N/A')} PRODUCT_IMAGE: {row.get('image', 'N/A')}\n"
    
    return summary
