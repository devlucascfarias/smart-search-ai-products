const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
const API_URL = API_BASE.endsWith('/') ? API_BASE.slice(0, -1) : API_BASE;

const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const categoryList = document.getElementById('categoryList');
const productGrid = document.getElementById('productGrid');
const sectionTitle = document.getElementById('sectionTitle');
const heroSection = document.getElementById('heroSection');
const aiSection = document.getElementById('aiSection');
const aiResponseText = document.getElementById('aiResponseText');
const loader = document.getElementById('loader');
const reportSection = document.getElementById('reportSection');
const reportBtn = document.getElementById('reportBtn');
const reportBtnFooter = document.getElementById('reportBtnFooter');
const logoBtn = document.getElementById('logoBtn');
const logoBtnFooter = document.getElementById('logoBtnFooter');
const newSearchBtn = document.getElementById('newSearchBtn');

const paginationContainer = document.getElementById('pagination');
const prevPageBtn = document.getElementById('prevPage');
const nextPageBtn = document.getElementById('nextPage');
const pageInfo = document.getElementById('pageInfo');

let currentCategory = 'Air Conditioners';
let currentPage = 1;
let totalPages = 1;

window.addEventListener('DOMContentLoaded', () => {
  loadCategories();
  loadFeatured();
  
  reportBtn.addEventListener('click', showReport);
  if (reportBtnFooter) reportBtnFooter.addEventListener('click', showReport);

  newSearchBtn.addEventListener('click', () => {
    showHome();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  
  const handleHomeClick = (e) => {
    e.preventDefault();
    showHome();
  };
  
  logoBtn.addEventListener('click', handleHomeClick);
  if (logoBtnFooter) logoBtnFooter.addEventListener('click', handleHomeClick);

  // Search Suggestions Handlers
  document.querySelectorAll('.suggestion-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      searchInput.value = pill.textContent;
      handleAISearch();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });
});

function showReport() {
  ++currentRequestId; 
  heroSection.classList.add('hidden');
  aiSection.classList.add('hidden');
  productGrid.classList.add('hidden');
  sectionTitle.classList.add('hidden');
  paginationContainer.classList.add('hidden');
  reportSection.classList.remove('hidden');
  
  // Mark category as inactive
  document.querySelectorAll('.category-item').forEach(el => el.classList.remove('active'));
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showHome() {
  reportSection.classList.add('hidden');
  heroSection.classList.remove('hidden');
  productGrid.classList.remove('hidden');
  sectionTitle.classList.remove('hidden');
  
  const featuredItem = document.getElementById('featuredItem');
  selectCategory('Air Conditioners', featuredItem);
}

async function loadCategories() {
  const featuredItem = document.getElementById('featuredItem');
  featuredItem.onclick = () => selectCategory('Air Conditioners', featuredItem);

  try {
    const response = await fetch(`${API_URL}/categories`);
    const categories = await response.json();
    
    categories.slice(0, 40).forEach(cat => {
      if (cat.id === 'Air Conditioners') return;
      const li = document.createElement('li');
      li.className = 'category-item';
      li.textContent = cat.name;
      li.onclick = () => selectCategory(cat.id, li);
      categoryList.appendChild(li);
    });
  } catch (error) {
    console.error('Erro ao carregar categorias:', error);
  }
}

async function loadFeatured() {
  const featuredItem = document.getElementById('featuredItem');
  selectCategory('Air Conditioners', featuredItem); 
}

let currentRequestId = 0;

async function selectCategory(category, element = null, page = 1) {
  const requestId = ++currentRequestId;
  currentCategory = category;
  currentPage = page;

  if (element) {
    document.querySelectorAll('.category-item').forEach(el => el.classList.remove('active'));
    element.classList.add('active');
  }
  
  if (category === 'Air Conditioners' && (!element || element.id === 'featuredItem')) {
    sectionTitle.textContent = 'Produtos em Destaque';
  } else {
    const label = element ? element.textContent : category;
    sectionTitle.textContent = `${label}`;
  }

  aiSection.classList.add('hidden');
  reportSection.classList.add('hidden');
  heroSection.classList.remove('hidden');
  paginationContainer.classList.add('hidden');
  productGrid.classList.remove('hidden');
  productGrid.innerHTML = '';
  loader.classList.remove('hidden');
  sectionTitle.classList.remove('hidden');

  try {
    const response = await fetch(`${API_URL}/products/${encodeURIComponent(category)}?page=${page}&page_size=20`);
    const data = await response.json();
    
    // Only update if this is still the most recent request
    if (requestId !== currentRequestId) return;

    totalPages = data.total_pages;
    renderProducts(data.products);
    updatePaginationUI();
  } catch (error) {
    if (requestId === currentRequestId) {
      productGrid.innerHTML = `<p style="color: red;">Erro ao carregar produtos desta categoria.</p>`;
    }
  } finally {
    if (requestId === currentRequestId) {
      loader.classList.add('hidden');
    }
  }
}

function updatePaginationUI() {
  // Never show pagination if the report or AI search results are visible
  const isReportVisible = !reportSection.classList.contains('hidden');
  const isAIVisible = !aiSection.classList.contains('hidden');
  
  if (totalPages <= 1 || isReportVisible || isAIVisible) {
    paginationContainer.classList.add('hidden');
    return;
  }
  
  paginationContainer.classList.remove('hidden');
  pageInfo.textContent = `Página ${currentPage} de ${totalPages}`;
  prevPageBtn.disabled = currentPage === 1;
  nextPageBtn.disabled = currentPage === totalPages;
}

prevPageBtn.onclick = () => {
  if (currentPage > 1) {
    selectCategory(currentCategory, null, currentPage - 1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

nextPageBtn.onclick = () => {
  if (currentPage < totalPages) {
    selectCategory(currentCategory, null, currentPage + 1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

async function handleAISearch() {
  const query = searchInput.value.trim();
  if (!query) return;

  ++currentRequestId; // Cancel any pending category loads
  productGrid.innerHTML = '';
  aiSection.classList.add('hidden');
  reportSection.classList.add('hidden');
  heroSection.classList.add('hidden');
  paginationContainer.classList.add('hidden');
  loader.classList.remove('hidden');
  paginationContainer.classList.add('hidden');
  
  sectionTitle.classList.add('hidden');

  try {
    const response = await fetch(`${API_URL}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: query }),
    });

    const data = await response.json();
    const rawResponse = data.response;

    const itemRegex = /\[ITEM\]([\s\S]*?)\[\/ITEM\]/g;
    const filterRegex = /\[FILTRO\](.*?)\[\/FILTRO\]/g;

    const itemMatches = [...rawResponse.matchAll(itemRegex)];
    const filterMatches = [...rawResponse.matchAll(filterRegex)];
    
    let cleanMessage = rawResponse
      .replace(itemRegex, '')
      .replace(filterRegex, '')
      .trim();

    cleanMessage = cleanMessage
      .replace(/\n{3,}/g, '\n\n')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/==(.*?)==/g, '<mark>$1</mark>')
      .replace(/\n/g, '<br>');

    aiSection.classList.remove('hidden');
    aiResponseText.innerHTML = cleanMessage;

    // Render Filters
    const filterContainer = document.createElement('div');
    filterContainer.className = 'ai-filters-container';
    filterMatches.forEach(match => {
      const term = match[1];
      const btn = document.createElement('button');
      btn.className = 'ai-filter-btn';
      btn.textContent = term;
      btn.onclick = () => {
        searchInput.value = term;
        handleAISearch();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      };
      filterContainer.appendChild(btn);
    });
    
    if (filterMatches.length > 0) {
      aiResponseText.appendChild(filterContainer);
    }

    const suggestedProducts = itemMatches.map(match => {
      const content = match[1];
      
      // Improved extraction using more specific regex and cleaning
      const nameMatch = content.match(/NOME:\s*(.*?)(?:\n|$)/);
      const priceMatch = content.match(/PRICE:\s*(.*?)(?:\n|$)/);
      const ratingMatch = content.match(/RATING:\s*(.*?)(?:\n|$)/);
      const imageMatch = content.match(/!\[.*?\]\((.*?)\)/);

      const name = nameMatch ? nameMatch[1].trim() : 'Produto';
      let price = priceMatch ? priceMatch[1].trim() : '--';
      let rating = ratingMatch ? ratingMatch[1].trim() : '4.0';
      
      // Try to get URL from Markdown format, fallback to raw URL if IMAGEM line exists
      let imageUrl = '';
      if (imageMatch) {
        imageUrl = imageMatch[1].trim();
      } else {
        const rawImageMatch = content.match(/IMAGEM:\s*(https?:\/\/\S+)/);
        imageUrl = rawImageMatch ? rawImageMatch[1].trim() : '';
      }

      // Clean up price/rating if they still contain garbage pipes from older LLM responses
      if (price.includes('|')) price = price.split('|')[0].trim();
      if (rating.includes('|')) rating = rating.split('|')[0].trim();

      return {
        name,
        actual_price: price,
        ratings: rating,
        image: imageUrl,
        isSuggestion: true
      };
    });

    if (suggestedProducts.length > 0) {
      paginationContainer.classList.add('hidden');
      renderProducts(suggestedProducts);
    } else {
      productGrid.innerHTML = '';
      sectionTitle.classList.add('hidden');
    }

  } catch (error) {
    console.error(error);
  } finally {
    loader.classList.add('hidden');
    paginationContainer.classList.add('hidden'); // Garante que paginação fique oculta
  }
}

function renderProducts(products) {
  productGrid.innerHTML = '';
  
  if (products.length === 0) {
    if (!aiSection.classList.contains('hidden') === false) {
       productGrid.innerHTML = '<p>No products found in this section.</p>';
    }
    return;
  }

  products.forEach(p => {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    card.innerHTML = `
      <div class="product-img-wrapper">
        <img src="${p.image}" alt="${p.name}" onerror="this.src='https://placehold.co/300x300?text=Indisponível'">
      </div>
      <div class="product-details">
        <div class="rating">
          ${p.ratings || '3.5'} ★
        </div>
        <div class="name" title="${p.name}">${p.name}</div>
        <div class="price">${p.actual_price || '--'}</div>
        <button class="buy-btn">Ver Detalhes</button>
      </div>
    `;
    productGrid.appendChild(card);
  });
}

searchBtn.addEventListener('click', handleAISearch);
searchInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') handleAISearch();
});
