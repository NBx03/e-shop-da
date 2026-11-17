/**
 * ДА! - Telegram Mini App & Browser Frontend Client (ООО «ДА»)
 * Fullstack Python Internship
 */

let allProducts = [];
let activeCategory = 'all';
let searchQuery = '';
let sortBy = 'popular';
let cart = JSON.parse(localStorage.getItem('da_cart') || localStorage.getItem('voltstore_cart') || '{}');

// Telegram WebApp reference & initialization
const tgApp = window.Telegram?.WebApp;

// Safe Haptic Feedback helper
function haptic(type = 'impact', style = 'light') {
  try {
    if (!tgApp?.HapticFeedback) return;
    if (type === 'impact') {
      tgApp.HapticFeedback.impactOccurred(style); // 'light', 'medium', 'heavy', 'rigid', 'soft'
    } else if (type === 'notification') {
      tgApp.HapticFeedback.notificationOccurred(style); // 'error', 'success', 'warning'
    } else if (type === 'selection') {
      tgApp.HapticFeedback.selectionChanged();
    }
  } catch (e) {
    // Non-telegram browser fallback
  }
}

// Telegram Closing Confirmation
function updateTelegramClosingConfirmation() {
  try {
    const hasItems = Object.keys(cart).length > 0;
    const isModalOpen = !document.getElementById('product-modal')?.classList.contains('hidden') ||
                        !document.getElementById('preorder-modal')?.classList.contains('hidden') ||
                        !document.getElementById('cart-drawer')?.classList.contains('hidden');
    if (hasItems || isModalOpen) {
      tgApp?.enableClosingConfirmation?.();
    } else {
      tgApp?.disableClosingConfirmation?.();
    }
  } catch (e) {}
}

// Telegram Native BackButton integration
function updateTelegramBackButton() {
  try {
    if (!tgApp?.BackButton) return;
    const isProductOpen = !document.getElementById('product-modal')?.classList.contains('hidden');
    const isPreorderOpen = !document.getElementById('preorder-modal')?.classList.contains('hidden');
    const isCartOpen = !document.getElementById('cart-drawer')?.classList.contains('hidden');

    if (isProductOpen || isPreorderOpen || isCartOpen) {
      tgApp.BackButton.show();
    } else {
      tgApp.BackButton.hide();
    }
  } catch (e) {}
}

function handleTelegramBackClick() {
  haptic('impact', 'light');
  if (!document.getElementById('preorder-modal')?.classList.contains('hidden')) {
    closePreorderModal();
  } else if (!document.getElementById('product-modal')?.classList.contains('hidden')) {
    closeProductModal();
  } else if (!document.getElementById('cart-drawer')?.classList.contains('hidden')) {
    const isCartStep2 = !document.getElementById('cart-step-2')?.classList.contains('hidden');
    if (isCartStep2) {
      showCartStep(1);
    } else {
      toggleCart(false);
    }
  }
}

// Phone mask & validation helpers
function validatePhone(phone) {
  if (!phone || typeof phone !== 'string') return false;
  if (/[a-zA-Zа-яА-ЯёЁ]/.test(phone)) return false;
  const digits = phone.replace(/\D/g, '');
  return digits.length >= 10 && digits.length <= 15;
}

function formatPhoneValue(value) {
  const digits = value.replace(/\D/g, '');
  if (!digits) return '';

  let res = '+7 ';
  let body = digits;
  if (digits.startsWith('7') || digits.startsWith('8')) {
    body = digits.substring(1);
  }

  if (body.length > 0) res += '(' + body.substring(0, 3);
  if (body.length >= 3) res += ') ' + body.substring(3, 6);
  if (body.length >= 6) res += '-' + body.substring(6, 8);
  if (body.length >= 8) res += '-' + body.substring(8, 10);

  return res;
}

function setupPhoneMask(inputId) {
  const input = document.getElementById(inputId);
  if (!input) return;

  input.addEventListener('input', () => {
    const raw = input.value;
    const digitsOnly = raw.replace(/\D/g, '');
    if (!digitsOnly) {
      input.value = '';
      return;
    }
    input.value = formatPhoneValue(raw);
    input.classList.remove('border-red-500', 'ring-2', 'ring-red-200');
  });

  input.addEventListener('focus', () => {
    input.classList.remove('border-red-500', 'ring-2', 'ring-red-200');
  });
}

document.addEventListener('DOMContentLoaded', () => {
  // Expand Mini App to full height
  try {
    tgApp?.ready?.();
    tgApp?.expand?.();
    if (tgApp?.BackButton) {
      tgApp.BackButton.onClick(handleTelegramBackClick);
    }
  } catch (e) {}

  initUserFromTelegram();
  setupPhoneMask('preorder-phone');
  setupPhoneMask('order-phone');
  loadProducts();
  updateCartBadge();
  checkStartAppParam();
  updateTelegramClosingConfirmation();
  updateTelegramBackButton();
  if (window.lucide) lucide.createIcons();
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

// Render product grid matching Figma
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
    
    // Status badges matching Figma iOS style
    let statusClass = 'bg-[#DCFCE7] text-[#15803D] border border-[#BBF7D0]';
    if (prod.status === 'on_the_way') statusClass = 'bg-[#FEF3C7] text-[#B45309] border border-[#FDE68A]';
    if (prod.status === 'preorder') statusClass = 'bg-[#EEEDFC] text-[#4F46E5] border border-[#C7D2FE]';

    const oldPriceHtml = prod.old_price 
      ? `<span class="text-xs text-slate-400 line-through">${formatPrice(prod.old_price)} ₽</span>` 
      : '';

    // Action button matching Figma
    let actionBtnHtml = '';
    if (prod.status === 'preorder') {
      actionBtnHtml = `
        <button onclick="event.stopPropagation(); haptic('impact', 'medium'); openPreorderModal(${prod.id}, '${escapeHtml(prod.title)}')"
          class="w-full py-2.5 px-3 rounded-xl bg-[#EEEDFC] hover:bg-indigo-100 text-[#4F46E5] border border-indigo-200 text-xs sm:text-sm font-bold transition flex items-center justify-center gap-1.5 active:scale-95 shadow-2xs">
          <span>Хочу такой 🔥</span>
        </button>
      `;
    } else if (inCartQty > 0) {
      actionBtnHtml = `
        <div onclick="event.stopPropagation()" class="flex items-center justify-between w-full bg-blue-50/80 border border-blue-200/80 rounded-xl p-1">
          <button onclick="haptic('impact', 'light'); updateCartQuantity(${prod.id}, -1)" class="w-7 h-7 rounded-lg bg-white shadow-2xs text-blue-700 font-black flex items-center justify-center hover:bg-slate-50 transition active:scale-90">-</button>
          <span class="text-xs sm:text-sm font-bold text-blue-900">${inCartQty} шт</span>
          <button onclick="haptic('impact', 'light'); updateCartQuantity(${prod.id}, 1)" class="w-7 h-7 rounded-lg bg-white shadow-2xs text-blue-700 font-black flex items-center justify-center hover:bg-slate-50 transition active:scale-90">+</button>
        </div>
      `;
    } else {
      actionBtnHtml = `
        <button onclick="event.stopPropagation(); haptic('impact', 'medium'); addToCart(${prod.id})"
          class="w-full py-2.5 px-3 rounded-xl bg-[#2481CC] hover:bg-blue-600 text-white text-xs sm:text-sm font-bold transition shadow-2xs flex items-center justify-center gap-1.5 active:scale-95">
          <i data-lucide="shopping-bag" class="w-4 h-4"></i>
          <span>В корзину</span>
        </button>
      `;
    }

    return `
      <div onclick="haptic('impact', 'light'); openProductModal(${prod.id})" class="bg-white rounded-2xl p-2.5 sm:p-3.5 border border-slate-200/90 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between group cursor-pointer">
        <div>
          <!-- Thumbnail with studio render and status badge -->
          <div class="relative aspect-square rounded-xl bg-[#F8FAFC] border border-slate-100 overflow-hidden mb-2 p-2 sm:p-3 flex items-center justify-center">
            <img src="${prod.main_image}" alt="${escapeHtml(prod.title)}" loading="lazy" class="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300">
            <span class="absolute top-1.5 left-1.5 px-2 py-0.5 rounded-full text-[9px] sm:text-[10px] font-bold shadow-2xs ${statusClass}">
              ${prod.status_label.toUpperCase()}
            </span>
          </div>

          <!-- Category and Title -->
          <span class="text-[10px] font-bold text-blue-600 uppercase tracking-wider block">${prod.category_name}</span>
          <h3 class="text-xs sm:text-sm font-bold text-slate-900 line-clamp-2 min-h-[2rem] sm:min-h-[2.5rem] mt-0.5 leading-snug group-hover:text-blue-600 transition-colors">${escapeHtml(prod.title)}</h3>
        </div>

        <div class="mt-2 sm:mt-2.5 space-y-2">
          <!-- Price -->
          <div class="flex items-baseline gap-1.5 flex-wrap">
            <span class="text-sm sm:text-base font-black text-slate-900 tracking-tight">${formatPrice(prod.price)} ₽</span>
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

// Category tabs matching Figma
function selectCategory(catId) {
  haptic('selection');
  activeCategory = catId;
  document.querySelectorAll('.category-btn').forEach(btn => {
    const match = btn.getAttribute('data-cat-id') === String(catId);
    if (match) {
      btn.className = 'category-btn px-4 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all bg-[#2481CC] text-white shadow-sm';
    } else {
      btn.className = 'category-btn px-4 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 shadow-2xs';
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

// Custom Sorting dropdown
function toggleSortMenu() {
  haptic('selection');
  const menu = document.getElementById('sort-menu');
  const chevron = document.getElementById('sort-chevron');
  if (!menu) return;

  const isOpen = !menu.classList.contains('hidden');
  if (isOpen) {
    menu.classList.add('hidden');
    if (chevron) chevron.style.transform = 'rotate(0deg)';
  } else {
    menu.classList.remove('hidden');
    if (chevron) chevron.style.transform = 'rotate(180deg)';
    if (window.lucide) lucide.createIcons();
  }
}

function applySort(val, label) {
  haptic('selection');
  sortBy = val;
  const labelEl = document.getElementById('sort-label');
  if (labelEl) labelEl.textContent = label;

  ['popular', 'price_asc', 'price_desc'].forEach(opt => {
    const checkEl = document.getElementById(`sort-check-${opt}`);
    if (checkEl) {
      if (opt === val) checkEl.classList.remove('hidden');
      else checkEl.classList.add('hidden');
    }
  });

  const menu = document.getElementById('sort-menu');
  const chevron = document.getElementById('sort-chevron');
  if (menu) menu.classList.add('hidden');
  if (chevron) chevron.style.transform = 'rotate(0deg)';

  loadProducts();
}

// Close sort menu on click outside
document.addEventListener('click', (e) => {
  const container = document.getElementById('sort-dropdown-container');
  const menu = document.getElementById('sort-menu');
  const chevron = document.getElementById('sort-chevron');
  if (container && menu && !container.contains(e.target)) {
    menu.classList.add('hidden');
    if (chevron) chevron.style.transform = 'rotate(0deg)';
  }
});

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
      prod.status === 'in_stock' ? 'bg-[#DCFCE7] text-[#15803D] border border-[#BBF7D0]' :
      prod.status === 'on_the_way' ? 'bg-[#FEF3C7] text-[#B45309] border border-[#FDE68A]' : 'bg-[#EEEDFC] text-[#4F46E5] border border-[#C7D2FE]'
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
        <button onclick="closeProductModal(); haptic('impact', 'medium'); openPreorderModal(${prod.id}, '${escapeHtml(prod.title)}')"
          class="w-full py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl transition shadow-md flex items-center justify-center gap-2 active:scale-98">
          <i data-lucide="flame" class="w-5 h-5"></i>
          <span>Оставить заявку «Хочу такой»</span>
        </button>
      `;
    } else {
      actionBar.innerHTML = `
        <button onclick="addToCart(${prod.id}); closeProductModal(); toggleCart(true);"
          class="w-full py-3.5 bg-[#2481CC] hover:bg-blue-600 text-white font-bold rounded-xl transition shadow-md flex items-center justify-center gap-2 active:scale-98">
          <i data-lucide="shopping-bag" class="w-5 h-5"></i>
          <span>Добавить в корзину за ${formatPrice(prod.price)} ₽</span>
        </button>
      `;
    }

    if (window.lucide) lucide.createIcons();
    document.getElementById('product-modal').classList.remove('hidden');
    updateTelegramBackButton();
    updateTelegramClosingConfirmation();
  } catch (err) {
    console.error('Error opening product modal:', err);
  }
}

function closeProductModal() {
  document.getElementById('product-modal').classList.add('hidden');
  updateTelegramBackButton();
  updateTelegramClosingConfirmation();
}

// ================= PREORDER REQUEST MODAL ("ХОЧУ ТАКОЙ") =================
function openPreorderModal(prodId, title) {
  document.getElementById('preorder-product-id').value = prodId;
  document.getElementById('preorder-product-name').textContent = title;
  document.getElementById('preorder-modal').classList.remove('hidden');
  updateTelegramBackButton();
  updateTelegramClosingConfirmation();
}

function closePreorderModal() {
  document.getElementById('preorder-modal').classList.add('hidden');
  updateTelegramBackButton();
  updateTelegramClosingConfirmation();
}

async function handlePreorderSubmit(e) {
  e.preventDefault();
  const prodId = document.getElementById('preorder-product-id').value;
  const name = document.getElementById('preorder-name').value.trim();
  const phone = document.getElementById('preorder-phone').value.trim();
  const phoneInput = document.getElementById('preorder-phone');
  const btn = document.getElementById('preorder-submit-btn');

  if (!validatePhone(phone)) {
    haptic('notification', 'error');
    phoneInput.classList.add('border-red-500', 'ring-2', 'ring-red-200');
    phoneInput.focus();
    alert('Пожалуйста, введите корректный номер телефона (например, +7 999 123-45-67). Номер не должен содержать буквы.');
    return;
  }

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
      haptic('notification', 'success');
      alert('Заявка принята! Мы оповестим вас, когда товар прибудет.');
      closePreorderModal();
    } else {
      haptic('notification', 'error');
      alert(data.error || 'Ошибка при отправке');
    }
  } catch (err) {
    haptic('notification', 'error');
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
  localStorage.setItem('da_cart', JSON.stringify(cart));
  updateCartBadge();
  updateTelegramClosingConfirmation();
}

function updateCartBadge() {
  const badge = document.getElementById('cart-badge');
  const bottomBar = document.getElementById('bottom-cart-bar');
  const bottomCount = document.getElementById('bottom-cart-count');
  const bottomTotal = document.getElementById('bottom-cart-total');

  const totalCount = Object.values(cart).reduce((sum, itm) => sum + itm.quantity, 0);
  const totalAmount = Object.values(cart).reduce((sum, itm) => sum + (itm.price * itm.quantity), 0);

  if (totalCount > 0) {
    if (badge) {
      badge.textContent = totalCount;
      badge.classList.remove('hidden');
      badge.classList.add('flex');
    }
    if (bottomBar) {
      bottomBar.classList.remove('hidden');
      bottomBar.classList.add('flex');
      if (bottomCount) bottomCount.textContent = `Корзина (${totalCount})`;
      if (bottomTotal) bottomTotal.textContent = `${formatPrice(totalAmount)} ₽ →`;
    }
  } else {
    if (badge) badge.classList.add('hidden');
    if (bottomBar) {
      bottomBar.classList.add('hidden');
      bottomBar.classList.remove('flex');
    }
  }
}

function toggleCart(open) {
  haptic('impact', 'light');
  const drawer = document.getElementById('cart-drawer');
  if (open) {
    showCartStep(1);
    renderCartDrawer();
    drawer.classList.remove('hidden');
  } else {
    drawer.classList.add('hidden');
  }
  updateTelegramBackButton();
  updateTelegramClosingConfirmation();
}

function showCartStep(step) {
  haptic('impact', 'light');
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
  updateTelegramBackButton();
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
        <img src="${itm.image}" class="w-14 h-14 rounded-xl object-contain bg-[#F8FAFC] border border-slate-100 flex-shrink-0 p-1">
        <div class="flex-1 min-w-0">
          <h4 class="text-xs font-bold text-slate-800 truncate">${escapeHtml(itm.title)}</h4>
          <span class="text-xs font-bold text-[#2481CC]">${formatPrice(itm.price)} ₽</span>
        </div>
        <div class="flex items-center gap-1.5 bg-slate-100 rounded-xl p-1">
          <button onclick="haptic('impact', 'light'); updateCartQuantity(${itm.id}, -1)" class="w-6 h-6 rounded-lg bg-white shadow-xs text-xs font-bold flex items-center justify-center active:scale-90">-</button>
          <span class="text-xs font-bold w-5 text-center">${itm.quantity}</span>
          <button onclick="haptic('impact', 'light'); updateCartQuantity(${itm.id}, 1)" class="w-6 h-6 rounded-lg bg-white shadow-xs text-xs font-bold flex items-center justify-center active:scale-90">+</button>
        </div>
      </div>
    `;
  }).join('');

  totalAmountEl.textContent = `${formatPrice(total)} ₽`;
  if (window.lucide) lucide.createIcons();
}

// Delivery UI logic
function updateDeliveryUI(method) {
  haptic('selection');
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
  const phoneInput = document.getElementById('order-phone');
  const delivery = document.querySelector('input[name="delivery"]:checked').value;
  const address = document.getElementById('order-address').value.trim();
  const payment = document.querySelector('input[name="payment"]:checked').value;
  const comment = document.getElementById('order-comment').value.trim();
  const submitBtn = document.getElementById('order-submit-btn');

  if (!validatePhone(phone)) {
    haptic('notification', 'error');
    phoneInput.classList.add('border-red-500', 'ring-2', 'ring-red-200');
    phoneInput.focus();
    alert('Пожалуйста, введите корректный номер телефона (например, +7 999 123-45-67). Номер не должен содержать буквы.');
    return;
  }

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
      haptic('notification', 'success');
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
      haptic('notification', 'error');
      alert(data.error || 'Ошибка при создании заказа');
      submitBtn.disabled = false;
      submitBtn.innerHTML = 'Подтвердить заказ';
    }
  } catch (err) {
    haptic('notification', 'error');
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
