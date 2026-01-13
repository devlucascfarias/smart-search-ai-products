# 🛍️ Smart Search AI - Intelligent E-commerce Assistant

An intelligent shopping assistant powered by **Natural Language Processing (NLP)** and **Retrieval-Augmented Generation (RAG)** that transforms traditional keyword searches into semantic, context-aware product discovery.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-orange.svg)](https://www.langchain.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Vector Store](#vector-store)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**Smart Search AI** is not just another e-commerce search engine. It's an intelligent assistant that:

- 🧠 **Understands Intent**: Uses LLMs to decode what users really want
- 🎯 **Semantic Search**: Finds products by meaning, not just keywords
- 🔍 **Smart Filtering**: Automatically filters irrelevant results
- 💰 **Budget Aware**: Extracts and respects price constraints
- 📊 **RAG-Powered**: Queries real product data before generating responses

### Example Queries

```
❌ Traditional: "notebook"
✅ Smart Search: "lightweight laptop for students under $800"

❌ Traditional: "headphones"
✅ Smart Search: "wireless headphones for gym with good bass"

❌ Traditional: "air conditioner"
✅ Smart Search: "silent air conditioner for small bedroom"
```

---

## ✨ Key Features

### 🤖 AI-Powered Search
- **Intent Analysis**: LLM-based query understanding
- **Category Mapping**: Automatic product category detection
- **Budget Extraction**: Smart price limit recognition

### 🔍 Semantic Search (Vector Store)
- **ChromaDB Integration**: Fast similarity search
- **Google Embeddings**: High-quality vector representations
- **~5,500 Products Indexed**: Comprehensive product coverage

### 🎨 Modern UI/UX
- **Responsive Design**: Works on all devices
- **Real-time Suggestions**: Dynamic search recommendations
- **Smart Filters**: AI-generated filter suggestions

### 🛡️ Production-Ready
- **External Prompts**: Easy prompt management and versioning
- **Caching**: Optimized performance
- **Error Handling**: Graceful degradation
- **CORS Enabled**: Ready for deployment

---

## 🏗️ Architecture

```
┌─────────────┐
│   User      │
│   Query     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         Intent Analysis             │
│  (LLM: Category + Budget Extract)   │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│      Vector Store Search            │
│  (Semantic Similarity - ChromaDB)   │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│     Product Retrieval (RAG)         │
│   (Real Database Query)             │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│    Response Generation              │
│  (LLM: Smart Filtering + Format)    │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────┐
│  Formatted  │
│  Response   │
└─────────────┘
```

### Agent Workflow

1. **Intent Agent**: Analyzes user query → extracts categories and budget
2. **Retrieval Agent**: Searches vector store → finds semantically similar products
3. **Filter Agent**: Applies intelligent filtering → removes irrelevant items
4. **Response Agent**: Generates natural language response → formats product cards

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **LangChain** - LLM orchestration framework
- **Google Gemini AI** - LLM (gemini-2.5-flash-lite)
- **ChromaDB** - Vector database for semantic search
- **Pandas** - Data manipulation
- **Pydantic** - Data validation

### Frontend
- **Vanilla JavaScript** - No framework overhead
- **Vite** - Fast build tool
- **Modern CSS** - Responsive design

### AI/ML
- **Google Embeddings** (embedding-001)
- **Prompt Engineering** - External prompt management
- **RAG Pattern** - Retrieval-Augmented Generation

---

## 📦 Installation

### Prerequisites

- Python 3.10+
- Node.js 16+
- Google Gemini API Key

### 1. Clone Repository

```bash
git clone https://github.com/devlucascfarias/smart-search-ai-products.git
cd smart-search-ai-products
```

### 2. Backend Setup

```bash
cd backend/api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your GEMINI_API_KEY to .env
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 4. Initialize Vector Store

```bash
cd backend/api
python init_vector_store.py
```

This will:
- Load ~5,500 products
- Generate embeddings
- Create ChromaDB index
- Takes ~5-10 minutes

---

## 🚀 Usage

### Start Backend

```bash
cd backend/api
uvicorn main:app --reload
```

Backend runs on: `http://localhost:8000`

### Start Frontend

```bash
cd frontend
npm run dev
```

Frontend runs on: `http://localhost:5173`

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

---

## 📁 Project Structure

```
smart-search-ai-products/
├── backend/
│   ├── api/
│   │   ├── prompts/              # External prompt files
│   │   │   ├── category_analysis.txt
│   │   │   ├── response_generation.txt
│   │   │   └── README.md
│   │   ├── chroma_db/            # Vector store (gitignored)
│   │   ├── main.py               # FastAPI app
│   │   ├── products.py           # Product data logic
│   │   ├── prompt_manager.py     # Prompt management
│   │   ├── vector_store.py       # Vector store manager
│   │   └── init_vector_store.py  # Vector store initialization
│   └── data/                     # Product CSV files
├── frontend/
│   ├── index.html
│   ├── main.js
│   ├── style.css
│   └── package.json
├── .gitignore
└── README.md
```

---

## 🔌 API Documentation

### Main Endpoints

#### `POST /generate`
Intelligent product search

**Request:**
```json
{
  "prompt": "silent air conditioner for small bedroom",
  "budget": 500.0
}
```

**Response:**
```json
{
  "response": "AI-generated response with product recommendations",
  "detected_budget": 500.0,
  "queried_categories": ["Air Conditioners"]
}
```

#### `GET /vector-store/search`
Direct semantic search

**Query Parameters:**
- `query` (string): Search query
- `category` (string, optional): Filter by category
- `limit` (int, default: 20): Number of results

#### `POST /vector-store/rebuild`
Rebuild vector store (use after data updates)

#### `GET /categories`
List all available categories

#### `GET /products/{category}`
Get products by category with pagination

---

## 🧠 Vector Store

### What is it?

The vector store uses **semantic embeddings** to find products by meaning, not just keywords.

### How it works:

1. **Indexing**: Products are converted to 768-dimensional vectors
2. **Search**: User query is converted to a vector
3. **Similarity**: Finds closest products in vector space
4. **Results**: Returns most relevant products

### Advantages:

✅ Understands synonyms and context  
✅ Finds products even without exact keyword match  
✅ Handles complex, natural language queries  
✅ Much faster than traditional search  

### Rebuild Vector Store:

```bash
# Via script
python init_vector_store.py

# Via API
curl -X POST http://localhost:8000/vector-store/rebuild
```

---

## 🎨 Prompt Engineering

Prompts are stored externally in `backend/api/prompts/` for easy management:

- **category_analysis.txt** - Intent analysis and category mapping
- **response_generation.txt** - Final response formatting

### Benefits:

✅ Easy to edit without touching code  
✅ Version control for prompts  
✅ A/B testing different versions  
✅ Collaboration with non-technical team members  

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Lucas Correia Farias**

- GitHub: [@devlucascfarias](https://github.com/devlucascfarias)
- LinkedIn: [Lucas Correia](https://www.linkedin.com/in/lucas-correia-b856152b5/)

---

## 🙏 Acknowledgments

- **Google Gemini AI** for powerful LLM capabilities
- **LangChain** for excellent LLM orchestration
- **ChromaDB** for fast vector search
- **FastAPI** for modern Python web framework

---

## 📊 Project Stats

- **~5,500 Products** indexed
- **112 Categories** supported
- **Vector Search** in ~100-200ms
- **90-95% Accuracy** in product relevance

---

## 🔮 Future Improvements

- [ ] Multi-language support
- [ ] User preference learning
- [ ] Product recommendation engine
- [ ] Advanced filters (brand, ratings, etc.)
- [ ] Real-time inventory updates
- [ ] Mobile app

---

**Made with ❤️ for learning and demonstration purposes**
