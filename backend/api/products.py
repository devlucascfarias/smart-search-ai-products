import os
import pandas as pd
from typing import List, Dict, Optional
from pydantic import BaseModel

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

# Conversion rate: 1 INR ≈ 0.066 BRL
INR_TO_BRL = 0.066

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

CATEGORY_TRANSLATIONS = {
    "All Appliances": "Eletrodomésticos",
    "All Car and Motorbike Products": "Automotivo e Motos",
    "All Electronics": "Eletrônicos",
    "All Exercise and Fitness": "Exercício e Fitness",
    "All Grocery and Gourmet Foods": "Mercearia e Gourmet",
    "All Home and Kitchen": "Casa e Cozinha",
    "All Pet Supplies": "Itens para Pets",
    "All Sports Fitness and Outdoors": "Esportes e Lazer",
    "Amazon Fashion": "Moda Amazon",
    "Air Conditioners": "Ar Condicionados",
    "All Video Games": "Video Games",
    "Baby Products": "Bebês",
    "Beauty and Personal Care": "Beleza e Cuidados",
    "Clothing and Accessories": "Roupas e Acessórios",
    "Computers and Accessories": "Computadores",
    "Industrial and Scientific": "Industrial e Científico",
    "Jewellery": "Joias",
    "Musical Instruments": "Instrumentos Musicais",
    "Office Products": "Escritório",
    "Pet Supplies": "Pets",
    "Software": "Software",
    "Sporting Goods": "Artigos Esportivos",
    "Toys and Games": "Brinquedos e Jogos",
    "Watches": "Relógios",
    "Cardio Equipment": "Equipamentos de Cardio",
    "Casual Shoes": "Calçados Casuais",
    "Clothing": "Vestuário",
    "Coffee Tea and Beverages": "Café, Chá e Bebidas",
    "Cricket": "Crquete",
    "Cycling": "Ciclismo",
    "Diapers": "Fraldas",
    "Diet and Nutrition": "Dieta e Nutrição",
    "Dog supplies": "Artigos para Cães",
    "Ethnic Wear": "Roupas Típicas",
    "Fashion and Silver Jewellery": "Joias de Prata e Moda",
    "Fitness Accessories": "Acessórios Fitness",
    "Garden and Outdoors": "Jardim e Exterior",
    "Health and Personal Care": "Saúde e Cuidados",
    "Home Audio": "Áudio para Casa",
    "Home Improvement": "Reforma e Casa",
    "Home Storage": "Organização e Casa",
    "Indoor Lighting": "Iluminação Interna",
    "Kitchen and Home Appliances": "Eletrodomésticos de Cozinha",
    "Laptops": "Notebooks",
    "Make-up": "Maquiagem",
    "Men's Accessories": "Acessórios Masculinos",
    "Men's Shoes": "Calçados Masculinos",
    "Mobile Phones": "Celulares",
    "Printers": "Impressoras",
    "Shoes": "Calçados",
    "Sports Shoes": "Tênis Esportivos",
    "Strollers and Prams": "Carrinhos de Bebê",
    "TV, Video and DVD": "TV e Vídeo",
    "Women's Accessories": "Acessórios Femininos",
    "Women's Shoes": "Calçados Femininos",
    "Refrigerators": "Geladeiras",
    "Washing Machines": "Máquinas de Lavar",
    "Televisions": "Televisões",
    "Cameras": "Câmeras",
    "Headphones": "Fones de Ouvido",
    "Speakers": "Alto-falantes",
    "Heating and Cooling Appliances": "Aquecimento e Refrigeração",
    "Personal Care Appliances": "Aparelhos de Cuidados Pessoais"
}

def translate_category(cat: str) -> str:
    return CATEGORY_TRANSLATIONS.get(cat, cat.replace("All ", "").replace("Products", "").strip())

def get_categories_with_names() -> str:
    """Retorna uma string formatada 'ID: Nome Traduzido' para o prompt da IA."""
    return "\n".join([f"- {cat}: {translate_category(cat)}" for cat in ALL_CATEGORIES])

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
        max_price_inr = max_price / INR_TO_BRL
        filtered_df = filtered_df[filtered_df['actual_price'].apply(clean_price) <= max_price_inr]

    if filtered_df.empty:
        return "NADA_ENCONTRADO"
    
    products = filtered_df.head(30)
    
    summary = f"Real Products Available in category '{category}':\n"
    for _, row in products.iterrows():
        price_inr = clean_price(row.get('actual_price', '0'))
        price_brl = price_inr * INR_TO_BRL
        summary += f"- Name: {row['name']} | PRICE: R$ {price_brl:.2f} | Rating: {row.get('ratings', 'N/A')} | Image: {row.get('image', 'N/A')}\n"
    
    return summary
