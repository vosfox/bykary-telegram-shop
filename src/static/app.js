// Telegram WebApp initialization
let tg = window.Telegram.WebApp;
tg.expand();

// Close WebApp function
function closeWebApp() {
    if (tg && tg.close) {
        tg.close();
    }
}

// Global state
let products = [];
let cart = [];
let currentCategory = 'all';
let userId = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    try {
        // Get user ID from Telegram
        if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
            userId = tg.initDataUnsafe.user.id.toString();
        } else {
            // Fallback for testing
            userId = 'demo_user';
        }

        showLoading(true);
        
        // Load products and cart
        await Promise.all([
            loadProducts(),
            loadCart()
        ]);
        
        showLoading(false);
        
        // Set up form submission
        document.getElementById('orderForm').addEventListener('submit', handleOrderSubmit);
        
    } catch (error) {
        console.error('Initialization error:', error);
        showLoading(false);
        showError('Ошибка загрузки приложения');
    }
}

async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        if (!response.ok) throw new Error('Failed to load products');
        
        products = await response.json();
        renderProducts();
    } catch (error) {
        console.error('Error loading products:', error);
        showError('Ошибка загрузки товаров');
    }
}

async function loadCart() {
    try {
        const response = await fetch(`/api/cart/${userId}`);
        if (!response.ok) throw new Error('Failed to load cart');
        
        cart = await response.json();
        updateCartCount();
    } catch (error) {
        console.error('Error loading cart:', error);
    }
}

function renderProducts() {
    const grid = document.getElementById('productsGrid');
    
    let filteredProducts = products;
    if (currentCategory !== 'all') {
        filteredProducts = products.filter(p => p.category === currentCategory);
    }
    
    if (filteredProducts.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <h3>Товары не найдены</h3>
                <p>В этой категории пока нет товаров</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = filteredProducts.map(product => `
        <div class="product-card">
            <div class="product-image">
                ${renderProductImages(product)}
            </div>
            <div class="product-info">
                <div class="product-name">${product.name}</div>
                <div class="product-price">${formatPrice(product.price)} ₽</div>
                <div class="product-controls">
                    <select class="size-select" id="size-${product.id}">
                        ${product.sizes.map(size => `<option value="${size}">${size}</option>`).join('')}
                    </select>
                </div>
                <button class="add-to-cart-btn" onclick="addToCart(${product.id})">
                    Добавить в корзину
                </button>
            </div>
        </div>
    `).join('');
}

function showCategory(category) {
    currentCategory = category;
    
    // Update navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Show products view
    showView('products');
    renderProducts();
}

async function addToCart(productId) {
    try {
        const sizeSelect = document.getElementById(`size-${productId}`);
        const size = sizeSelect.value;
        
        const response = await fetch('/api/cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                product_id: productId,
                size: size,
                quantity: 1
            })
        });
        
        if (!response.ok) throw new Error('Failed to add to cart');
        
        await loadCart();
        showNotification('Товар добавлен в корзину');
        
        // Haptic feedback
        if (tg.HapticFeedback) {
            tg.HapticFeedback.impactOccurred('light');
        }
        
    } catch (error) {
        console.error('Error adding to cart:', error);
        showError('Ошибка добавления в корзину');
    }
}

function showCart() {
    showView('cart');
    renderCart();
}

function renderCart() {
    const cartItems = document.getElementById('cartItems');
    const totalAmount = document.getElementById('totalAmount');
    
    if (cart.length === 0) {
        cartItems.innerHTML = `
            <div class="empty-state">
                <h3>Корзина пуста</h3>
                <p>Добавьте товары из каталога</p>
            </div>
        `;
        totalAmount.textContent = '0';
        return;
    }
    
    let total = 0;
    
    cartItems.innerHTML = cart.map(item => {
        const itemTotal = item.product.price * item.quantity;
        total += itemTotal;
        
        return `
            <div class="cart-item">
                <div class="cart-item-image">
                    <img src="${item.product.image_url}" alt="${item.product.name}" 
                         onerror="this.style.display='none'; this.parentElement.innerHTML='Фото';">
                </div>
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.product.name}</div>
                    <div class="cart-item-details">
                        Размер: ${item.size} | ${formatPrice(item.product.price)} ₽
                    </div>
                </div>
                <div class="cart-item-controls">
                    <button class="quantity-btn" onclick="updateQuantity(${item.id}, ${item.quantity - 1})">-</button>
                    <span class="quantity">${item.quantity}</span>
                    <button class="quantity-btn" onclick="updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
                    <button class="remove-btn" onclick="removeFromCart(${item.id})">Удалить</button>
                </div>
            </div>
        `;
    }).join('');
    
    totalAmount.textContent = formatPrice(total);
}

async function updateQuantity(itemId, newQuantity) {
    if (newQuantity <= 0) {
        await removeFromCart(itemId);
        return;
    }
    
    try {
        const response = await fetch(`/api/cart/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                quantity: newQuantity
            })
        });
        
        if (!response.ok) throw new Error('Failed to update quantity');
        
        await loadCart();
        renderCart();
        
    } catch (error) {
        console.error('Error updating quantity:', error);
        showError('Ошибка обновления количества');
    }
}

async function removeFromCart(itemId) {
    try {
        const response = await fetch(`/api/cart/${itemId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to remove from cart');
        
        await loadCart();
        renderCart();
        showNotification('Товар удален из корзины');
        
    } catch (error) {
        console.error('Error removing from cart:', error);
        showError('Ошибка удаления товара');
    }
}

function showCheckout() {
    showView('checkout');
}

async function handleOrderSubmit(event) {
    event.preventDefault();
    
    if (cart.length === 0) {
        showError('Корзина пуста');
        return;
    }
    
    const formData = new FormData(event.target);
    const orderData = {
        user_id: userId,
        name: formData.get('customerName') || document.getElementById('customerName').value,
        phone: formData.get('customerPhone') || document.getElementById('customerPhone').value,
        city: formData.get('customerCity') || document.getElementById('customerCity').value,
        comment: formData.get('customerComment') || document.getElementById('customerComment').value
    };
    
    try {
        showLoading(true);
        
        const response = await fetch('/api/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Failed to create order');
        }
        
        showLoading(false);
        
        // Show success message
        alert(result.message);
        
        // Reset form and cart
        event.target.reset();
        await loadCart();
        showView('products');
        
        // Send data back to bot
        if (tg.sendData) {
            tg.sendData(JSON.stringify({
                type: 'order_completed',
                order_id: result.order_id,
                total_amount: result.total_amount
            }));
        }
        
    } catch (error) {
        console.error('Error creating order:', error);
        showLoading(false);
        showError(error.message || 'Ошибка оформления заказа');
    }
}

function showView(viewName) {
    // Hide all views
    document.getElementById('productsGrid').classList.add('hidden');
    document.getElementById('cartView').classList.add('hidden');
    document.getElementById('checkoutForm').classList.add('hidden');
    
    // Show selected view
    switch (viewName) {
        case 'products':
            document.getElementById('productsGrid').classList.remove('hidden');
            break;
        case 'cart':
            document.getElementById('cartView').classList.remove('hidden');
            break;
        case 'checkout':
            document.getElementById('checkoutForm').classList.remove('hidden');
            break;
    }
}

function updateCartCount() {
    const count = cart.reduce((sum, item) => sum + item.quantity, 0);
    document.getElementById('cartCount').textContent = count;
}

function showLoading(show) {
    const loading = document.getElementById('loading');
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

function showNotification(message) {
    // Simple notification - could be enhanced
    if (tg.showAlert) {
        tg.showAlert(message);
    } else {
        alert(message);
    }
}

function showError(message) {
    console.error(message);
    if (tg.showAlert) {
        tg.showAlert('Ошибка: ' + message);
    } else {
        alert('Ошибка: ' + message);
    }
}

function renderProductImages(product) {
    const images = product.images || [product.image_url];
    
    if (images.length === 1) {
        return `<img src="${images[0]}" alt="${product.name}" 
                     onerror="this.style.display='none'; this.parentElement.innerHTML='Фото товара';">`;
    }
    
    // Если изображений несколько, создаем галерею с превью
    const primaryImage = images[0];
    return `
        <div class="image-gallery">
            <img src="${primaryImage}" alt="${product.name}" class="primary-image" id="primary-${product.id}"
                 onerror="this.style.display='none'; this.parentElement.innerHTML='Фото товара';">
            ${images.length > 1 ? `
                <div class="image-thumbnails">
                    ${images.map((img, index) => `
                        <img src="${img}" alt="${product.name} ${index + 1}" class="thumbnail ${index === 0 ? 'active' : ''}"
                             onclick="switchImage(${product.id}, '${img}', this)"
                             onerror="this.style.display='none';">
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `;
}

function switchImage(productId, imageUrl, thumbnail) {
    // Обновляем основное изображение
    const primaryImage = document.getElementById(`primary-${productId}`);
    if (primaryImage) {
        primaryImage.src = imageUrl;
    }
    
    // Обновляем активный thumbnail
    const container = thumbnail.parentElement;
    container.querySelectorAll('.thumbnail').forEach(thumb => thumb.classList.remove('active'));
    thumbnail.classList.add('active');
}

function formatPrice(price) {
    return new Intl.NumberFormat('ru-RU').format(price);
}

// Telegram WebApp event handlers
tg.onEvent('mainButtonClicked', function() {
    // Handle main button click if needed
});

tg.onEvent('backButtonClicked', function() {
    // Handle back button
    showView('products');
});

// Set main button
tg.MainButton.setText('Закрыть');
tg.MainButton.show();

