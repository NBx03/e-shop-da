/**
 * VoltStore - Telegram Mini App & Browser Frontend Client
 */

let allProducts = [];
let activeCategory = 'all';
let searchQuery = '';
let sortBy = 'popular';
let cart = JSON.parse(localStorage.getItem('voltstore_cart') || '{}');

// Telegram WebApp reference
const tgApp = window.Telegram?.WebApp;

document.addEventListener('DOMContentLoaded', () => {
  initUserFromTelegram();
  loadProducts();
  updateCartBadge();
  checkStartAppParam();
});

// Autofill name from Telegram user profile
function initUserFromTelegram() {
  if (tgApp?.initDataUnsafe?.user) {
    const user = tgApp.initDataUnsafe.user;
    const fullName = [user.first_name, user.last_name].filter(Boolean).join(' ');
    
    const nameInput = document.getElementById('order-name');
    if (nameInput && !nameInput.value) nameInput.value = fullName;

    const preorderName = document.getElementById('preorder-name');
    if (preorderName && !preorderName.value) preorderName.value = fullName;
  }
}

// Fetch products from backend
async function loadProducts() {
  const countLabel = document.getElementById('products-count-label');
  try {
    let url = `/api/products/?category=${activeCategory}&sort=${sortBy}`;
    if (searchQuery) url += `&q=${encodeURIComponent(searchQuery)}`;
    
    const res = await fetch(url);
    const data = await res.json();
    allProducts = data.products || [];
    renderProducts(allProducts);

    if (countLabel) {
      countLabel.textContent = `Показано товаров: ${allProducts.length}`;
    }
  } catch (err) {
    console.error('Failed to load products:', err);
    if (countLabel) countLabel.textContent = 'Ошибка загрузки каталога';
  }
}

// Render product grid
function renderProducts(products) {
  const grid = document.getElementById('products-grid');
  const emptyState = document.getElementById('empty-state');
  
  if (!products || products.length === 0) {
    grid.innerHTML = '';
    emptyState.classList.remove('hidden');
    return;
  }
  emptyState.classList.add('hidden');

  grid.innerHTML = products.map(prod => {
    const inCartQty = cart[prod.id]?.quantity || 0;
    
    // Status badges
    let statusClass = 'bg-emerald-500 text-white';
    if (prod.status === 'on_the_way') statusClass = 'bg-amber-500 text-white';
    if (prod.status === 'preorder') statusClass = 'bg-indigo-600 text-white';

    const oldPriceHtml = prod.old_price 
      ? `<span class="text-[11px] text-slate-400 line-through">${formatPrice(prod.old_price)} ₽</span>` 
      : '';

    // Action button
    let actionBtnHtml = '';
    if (prod.status === 'preorder') {
      actionBtnHtml = `
        <button onclick="event.stopPropagation(); openPreorderModal(${prod.id}, '${escapeHtml(prod.title)}')"
          class="w-full py-2 px-2.5 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-bold transition flex items-center justify-center gap-1">
          <i data-lucide="flame" class="w-3.5 h-3.5"></i>
          <span>Хочу такой</span>
        </button>
      `;
    } else if (inCartQty > 0) {
      actionBtnHtml = `
        <div onclick="event.stopPropagation()" class="flex items-center justify-between w-full bg-blue-50 rounded-xl p-1">
          <button onclick="updateCartQuantity(${prod.id}, -1)" class="w-7 h-7 rounded-lg bg-white shadow-xs text-blue-700 font-black flex items-center justify-center hover:bg-slate-50">-</button>
          <span class="text-xs font-bold text-blue-900">${inCartQty} шт</span>
          <button onclick="updateCartQuantity(${prod.id}, 1)" class="w-7 h-7 rounded-lg bg-white shadow-xs text-blue-700 font-black flex items-center justify-center hover:bg-slate-50">+</button>
        </div>
      `;
    } else {
      actionBtnHtml = `
        <button onclick="event.stopPropagation(); addToCart(${prod.id})"
          class="w-full py-2 px-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold transition shadow-xs flex items-center justify-center gap-1 active:scale-95">
          <i data-lucide="shopping-bag" class="w-3.5 h-3.5"></i>
          <span>В корзину</span>
        </button>
      `;
    }

    return `
      <div onclick="openProductModal(${prod.id})" class="tg-card rounded-2xl p-3 border border-slate-200/60 shadow-xs hover:shadow-md transition cursor-pointer flex flex-col justify-between group">
        <div>
          <!-- Thumbnail -->
          <div class="relative aspect-square rounded-xl bg-slate-100 overflow-hidden mb-2.5">
            <img src="${prod.main_image}" alt="${escapeHtml(prod.title)}" loading="lazy" class="w-full h-full object-cover group-hover:scale-105 transition duration-300">
            <span class="absolute top-2 left-2 px-2 py-0.5 rounded-full text-[10px] font-bold ${statusClass}">
              ${prod.status_label}
            </span>
          </div>

          <!-- Category and Title -->
          <span class="text-[10px] font-semibold text-blue-600 uppercase tracking-wider block">${prod.category_name}</span>
          <h3 class="text-xs font-bold text-slate-800 line-clamp-2 mt-0.5 leading-snug">${escapeHtml(prod.title)}</h3>
        </div>

        <div class="mt-3 space-y-2">
          <!-- Price -->
          <div>
            <div class="text-sm font-black text-slate-900">${formatPrice(prod.price)} ₽</div>
            ${oldPriceHtml}
          </div>

          <!-- Action -->
          ${actionBtnHtml}
        </div>
      </div>
    `;
  }).join('');

  if (window.lucide) lucide.createIcons();
}

// Category tabs
function selectCategory(catId) {
  activeCategory = catId;
  document.querySelectorAll('.category-btn').forEach(btn => {
    const match = btn.getAttribute('data-cat-id') === String(catId);
    if (match) {
      btn.className = 'category-btn px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all bg-blue-600 text-white shadow-sm';
    } else {
      btn.className = 'category-btn px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all bg-slate-100 hover:bg-slate-200 text-slate-700';
    }
  });
  loadProducts();
}

// Search debounce
let searchTimeout = null;
function handleSearch(val) {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    searchQuery = val.trim();
    loadProducts();
  }, 300);
}

// Sorting
function handleSort(val) {
  sortBy = val;
  loadProducts();
}

// ================= PRODUCT DETAIL MODAL =================
async function openProductModal(prodIdOrSlug) {
  try {
    const res = await fetch(`/api/products/${prodIdOrSlug}/`);
    if (!res.ok) return;
    const prod = await res.json();

    document.getElementById('modal-img').src = prod.gallery[0] || '';
    document.getElementById('modal-cat-name').textContent = prod.category_name;
    document.getElementById('modal-title').textContent = prod.title;
    document.getElementById('modal-price').textContent = `${formatPrice(prod.price)} ₽`;
    
    const oldPriceEl = document.getElementById('modal-old-price');
    if (prod.old_price) {
      oldPriceEl.textContent = `${formatPrice(prod.old_price)} ₽`;
      oldPriceEl.classList.remove('hidden');
    } else {
      oldPriceEl.classList.add('hidden');
    }

    const badge = document.getElementById('modal-status-badge');
    badge.textContent = prod.status_label;
    badge.className = `absolute top-3 left-3 px-2.5 py-1 rounded-full text-[11px] font-bold shadow-sm ${
      prod.status === 'in_stock' ? 'bg-emerald-500 text-white' :
      prod.status === 'on_the_way' ? 'bg-amber-500 text-white' : 'bg-indigo-600 text-white'
    }`;

    document.getElementById('modal-desc').textContent = prod.description;

    // Specs
    const specsContainer = document.getElementById('modal-specs-list');
    const specsKeys = Object.keys(prod.characteristics || {});
    if (specsKeys.length > 0) {
      specsContainer.innerHTML = specsKeys.map(k => `
        <div class="flex justify-between py-1.5">
          <span class="tg-hint">${escapeHtml(k)}</span>
          <span class="font-medium text-slate-800 text-right">${escapeHtml(String(prod.characteristics[k]))}</span>
        </div>
      `).join('');
      document.getElementById('modal-specs-container').classList.remove('hidden');
    } else {
      document.getElementById('modal-specs-container').classList.add('hidden');
    }

    // Action button
    const actionBar = document.getElementById('modal-action-bar');
    if (prod.status === 'preorder') {
      actionBar.innerHTML = `
        <button onclick="closeProductModal(); openPreorderModal(${prod.id}, '${escapeHtml(prod.title)}')"
          class="w-full py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl transition shadow-md flex items-center justify-center gap-2">
          <i data-lucide="flame" class="w-5 h-5"></i>
          <span>Оставить заявку «Хочу такой»</span>
        </button>
      `;
    } else {
      actionBar.innerHTML = `
        <button onclick="addToCart(${prod.id}); closeProductModal(); toggleCart(true);"
          class="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl transition shadow-md flex items-center justify-center gap-2">
          <i data-lucide="shopping-bag" class="w-5 h-5"></i>
          <span>Добавить в корзину за ${formatPrice(prod.price)} ₽</span>
        </button>
      `;
    }

    if (window.lucide) lucide.createIcons();
    document.getElementById('product-modal').classList.remove('hidden');
  } catch (err) {
    console.error('Error opening product modal:', err);
  }
}

function closeProductModal() {
  document.getElementById('product-modal').classList.add('hidden');
}

// ================= PREORDER REQUEST MODAL ("ХОЧУ ТАКОЙ") =================
function openPreorderModal(prodId, title) {
  document.getElementById('preorder-product-id').value = prodId;
  document.getElementById('preorder-product-name').textContent = title;
  document.getElementById('preorder-modal').classList.remove('hidden');
}

function closePreorderModal() {
  document.getElementById('preorder-modal').classList.add('hidden');
}

async function handlePreorderSubmit(e) {
  e.preventDefault();
  const prodId = document.getElementById('preorder-product-id').value;
  const name = document.getElementById('preorder-name').value;
  const phone = document.getElementById('preorder-phone').value;
  const btn = document.getElementById('preorder-submit-btn');

  btn.disabled = true;
  btn.textContent = 'Отправка заявки...';

  try {
    const payload = {
      product_id: prodId,
      name: name,
      phone: phone,
      initData: tgApp?.initData || ''
    };

    const res = await fetch('/api/preorder/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (res.ok && data.success) {
      alert('Заявка принята! Мы оповестим вас, когда товар прибудет.');
      closePreorderModal();
    } else {
      alert(data.error || 'Ошибка при отправке');
    }
  } catch (err) {
    alert('Ошибка сети: ' + err);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Отправить заявку';
  }
}

// ================= CART LOGIC (localStorage) =================
function addToCart(prodId) {
  const prod = allProducts.find(p => p.id === prodId);
  if (!prod) return;

  if (!cart[prodId]) {
    cart[prodId] = {
      id: prod.id,
      title: prod.title,
      price: prod.price,
      image: prod.main_image,
      quantity: 1
    };
  } else {
    cart[prodId].quantity += 1;
  }
  saveCart();
  renderProducts(allProducts);
}

function updateCartQuantity(prodId, delta) {
  if (!cart[prodId]) return;
  cart[prodId].quantity += delta;
  if (cart[prodId].quantity <= 0) {
    delete cart[prodId];
  }
  saveCart();
  renderProducts(allProducts);
  renderCartDrawer();
}

function saveCart() {
  localStorage.setItem('voltstore_cart', JSON.stringify(cart));
  updateCartBadge();
}

function updateCartBadge() {
  const badge = document.getElementById('cart-badge');
  const totalCount = Object.values(cart).reduce((sum, itm) => sum + itm.quantity, 0);
  if (totalCount > 0) {
    badge.textContent = totalCount;
    badge.classList.remove('hidden');
    badge.classList.add('flex');
  } else {
    badge.classList.add('hidden');
  }
}

function toggleCart(open) {
  const drawer = document.getElementById('cart-drawer');
  if (open) {
    showCartStep(1);
    renderCartDrawer();
    drawer.classList.remove('hidden');
  } else {
    drawer.classList.add('hidden');
  }
}

function showCartStep(step) {
  const step1 = document.getElementById('cart-step-1');
  const step2 = document.getElementById('cart-step-2');
  const backBtn = document.getElementById('cart-back-btn');
  const title = document.getElementById('cart-title');
  const checkoutBtn = document.getElementById('cart-checkout-btn');
  const submitBtn = document.getElementById('order-submit-btn');

  if (step === 1) {
    step1.classList.remove('hidden');
    step2.classList.add('hidden');
    backBtn.classList.add('hidden');
    title.textContent = 'Корзина';
    checkoutBtn.classList.remove('hidden');
    submitBtn.classList.add('hidden');
  } else {
    const items = Object.values(cart);
    if (items.length === 0) {
      alert('Корзина пуста');
      return;
    }
    step1.classList.add('hidden');
    step2.classList.remove('hidden');
    backBtn.classList.remove('hidden');
    title.textContent = 'Оформление заказа';
    checkoutBtn.classList.add('hidden');
    submitBtn.classList.remove('hidden');
  }
}

function renderCartDrawer() {
  const list = document.getElementById('cart-items-list');
  const emptyMsg = document.getElementById('cart-empty-msg');
  const totalAmountEl = document.getElementById('cart-total-amount');
  const checkoutBtn = document.getElementById('cart-checkout-btn');

  const items = Object.values(cart);
  if (items.length === 0) {
    list.innerHTML = '';
    emptyMsg.classList.remove('hidden');
    totalAmountEl.textContent = '0 ₽';
    checkoutBtn.classList.add('opacity-50', 'pointer-events-none');
    return;
  }

  emptyMsg.classList.add('hidden');
  checkoutBtn.classList.remove('opacity-50', 'pointer-events-none');

  let total = 0;
  list.innerHTML = items.map(itm => {
    const subtotal = itm.price * itm.quantity;
    total += subtotal;

    return `
      <div class="flex items-center gap-3 py-3">
        <img src="${itm.image}" class="w-14 h-14 rounded-xl object-cover bg-slate-100 flex-shrink-0">
        <div class="flex-1 min-w-0">
          <h4 class="text-xs font-bold text-slate-800 truncate">${escapeHtml(itm.title)}</h4>
          <span class="text-xs font-bold text-blue-600">${formatPrice(itm.price)} ₽</span>
        </div>
        <div class="flex items-center gap-1.5 bg-slate-100 rounded-xl p-1">
          <button onclick="updateCartQuantity(${itm.id}, -1)" class="w-6 h-6 rounded-lg bg-white shadow-xs text-xs font-bold flex items-center justify-center">-</button>
          <span class="text-xs font-bold w-5 text-center">${itm.quantity}</span>
          <button onclick="updateCartQuantity(${itm.id}, 1)" class="w-6 h-6 rounded-lg bg-white shadow-xs text-xs font-bold flex items-center justify-center">+</button>
        </div>
      </div>
    `;
  }).join('');

  totalAmountEl.textContent = `${formatPrice(total)} ₽`;
  if (window.lucide) lucide.createIcons();
}

// Delivery UI logic
function updateDeliveryUI(method) {
  const addressBlock = document.getElementById('address-block');
  const addressInput = document.getElementById('order-address');
  const codRadio = document.getElementById('payment-cod-radio');
  const codLabel = document.getElementById('payment-cod-label');
  const codHint = document.getElementById('cod-hint');

  if (method === 'pickup') {
    addressBlock.classList.add('hidden');
    addressInput.required = false;
  } else {
    addressBlock.classList.remove('hidden');
    addressInput.required = true;
  }

  // Postal rule: COD is forbidden for postal delivery
  if (method === 'postal') {
    codRadio.disabled = true;
    codLabel.classList.add('opacity-40', 'pointer-events-none');
    codHint.classList.remove('hidden');
    document.querySelector('input[name="payment"][value="online"]').checked = true;
  } else {
    codRadio.disabled = false;
    codLabel.classList.remove('opacity-40', 'pointer-events-none');
    codHint.classList.add('hidden');
  }
}

// Checkout submit
async function handleCheckoutSubmit(e) {
  e.preventDefault();
  const name = document.getElementById('order-name').value.trim();
  const phone = document.getElementById('order-phone').value.trim();
  const delivery = document.querySelector('input[name="delivery"]:checked').value;
  const address = document.getElementById('order-address').value.trim();
  const payment = document.querySelector('input[name="payment"]:checked').value;
  const comment = document.getElementById('order-comment').value.trim();
  const submitBtn = document.getElementById('order-submit-btn');

  const items = Object.values(cart).map(itm => ({
    id: itm.id,
    quantity: itm.quantity
  }));

  if (items.length === 0) {
    alert('Корзина пуста');
    return;
  }

  submitBtn.disabled = true;
  submitBtn.innerHTML = 'Оформление...';

  try {
    const payload = {
      customer_name: name,
      customer_phone: phone,
      delivery_method: delivery,
      delivery_address: address,
      payment_method: payment,
      comment: comment,
      items: items,
      initData: tgApp?.initData || ''
    };

    const res = await fetch('/orders/api/create/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (res.ok && data.success) {
      // Clear cart
      cart = {};
      saveCart();

      // Redirect to payment mock or order status
      if (data.payment_url) {
        window.location.href = data.payment_url;
      } else {
        window.location.href = `/orders/status/${data.order_id}/`;
      }
    } else {
      alert(data.error || 'Ошибка при создании заказа');
      submitBtn.disabled = false;
      submitBtn.innerHTML = 'Подтвердить заказ';
    }
  } catch (err) {
    alert('Ошибка сети: ' + err);
    submitBtn.disabled = false;
    submitBtn.innerHTML = 'Подтвердить заказ';
  }
}

// Check startapp parameter
function checkStartAppParam() {
  const urlParam = window.STARTAPP_PARAM || tgApp?.initDataUnsafe?.start_param;
  if (urlParam) {
    openProductModal(urlParam);
  }
}

// Helpers
function formatPrice(num) {
  return Number(num).toLocaleString('ru-RU');
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
