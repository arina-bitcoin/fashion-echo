// cart.js
class ShoppingCart {
    constructor() {
        this.items = [];
        this.isLoading = false;
        this.elements = this.initializeElements();
        this.attachEventListeners();
        this.loadCart();
    }

    initializeElements() {
        return {
            cartItems: document.getElementById('cart-items'),
            emptyCart: document.getElementById('empty-cart'),
            subtotal: document.getElementById('subtotal'),
            shipping: document.getElementById('shipping'),
            total: document.getElementById('total'),
            promoCode: document.getElementById('promo-code'),
            applyPromo: document.getElementById('apply-promo'),
            checkoutBtn: document.getElementById('checkout-btn'),
            continueShopping: document.getElementById('continue-shopping'),
            toast: document.getElementById('toast'),
            loadingIndicator: document.getElementById('loading-indicator') || this.createLoadingIndicator()
        };
    }

    createLoadingIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'loading-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 20px;
            border-radius: 8px;
            z-index: 1000;
            display: none;
        `;
        indicator.innerHTML = 'Загрузка...';
        document.body.appendChild(indicator);
        return indicator;
    }

    attachEventListeners() {
        if (this.elements.applyPromo) {
            this.elements.applyPromo.addEventListener('click', () => this.applyPromoCode());
        }
        
        if (this.elements.checkoutBtn) {
            this.elements.checkoutBtn.addEventListener('click', () => this.checkout());
        }
        
        if (this.elements.continueShopping) {
            this.elements.continueShopping.addEventListener('click', () => {
                window.location.href = 'index.html';
            });
        }

        // Обработка ввода промокода по Enter
        if (this.elements.promoCode) {
            this.elements.promoCode.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.applyPromoCode();
                }
            });
        }
    }

    async loadCart() {
        this.showLoading(true);
        
        try {
            // Пытаемся загрузить из API
            await this.loadCartFromServer();
        } catch (error) {
            console.warn('Не удалось загрузить корзину с сервера:', error);
            // Загружаем демо-данные
            this.loadDemoCart();
        } finally {
            this.showLoading(false);
        }
    }

    async loadCartFromServer() {
        // Эмуляция API запроса - замените на реальный эндпоинт
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Демо-данные (в реальном приложении здесь будет fetch к API)
        const demoCart = [
            {
                id: 1,
                name: 'Платье летнее',
                price: 1200,
                size: 'M',
                image: 'https://via.placeholder.com/300x300/F3E4D3/4B0505?text=Платье',
                quantity: 1,
                available: true
            },
            {
                id: 2,
                name: 'Джинсы классические',
                price: 800,
                size: '42',
                image: 'https://via.placeholder.com/300x300/F3E4D3/4B0505?text=Джинсы',
                quantity: 2,
                available: true
            },
            {
                id: 3,
                name: 'Куртка кожаная',
                price: 2500,
                size: 'L',
                image: 'https://via.placeholder.com/300x300/F3E4D3/4B0505?text=Куртка',
                quantity: 1,
                available: true
            }
        ];

        this.items = demoCart;
        this.renderCart();
        this.updateSummary();
        this.saveCartToLocalStorage();
    }

    loadDemoCart() {
        // Загрузка из localStorage или демо-данные
        const savedCart = localStorage.getItem('fashioneco-cart');
        if (savedCart) {
            this.items = JSON.parse(savedCart);
        } else {
            this.items = [
                {
                    id: 1,
                    name: 'Платье летнее',
                    price: 1200,
                    size: 'M',
                    image: 'https://via.placeholder.com/300x300/F3E4D3/4B0505?text=Платье',
                    quantity: 1,
                    available: true
                }
            ];
        }
        this.renderCart();
        this.updateSummary();
    }

    renderCart() {
        if (!this.elements.cartItems) return;

        if (this.items.length === 0) {
            this.showEmptyCart();
            return;
        }

        this.hideEmptyCart();
        
        this.elements.cartItems.innerHTML = this.items.map(item => `
            <div class="cart-item" data-id="${item.id}">
                <img src="${item.image}" alt="${item.name}" class="item-image">
                <div class="item-details">
                    <div class="item-name">${item.name}</div>
                    <div class="item-size">Размер: ${item.size}</div>
                    <div class="item-price">${item.price.toLocaleString()} ₽</div>
                    ${!item.available ? '<div class="item-unavailable">Нет в наличии</div>' : ''}
                </div>
                <div class="item-controls">
                    <div class="quantity-controls">
                        <button class="quantity-btn" onclick="cart.decreaseQuantity(${item.id})" 
                                ${item.quantity <= 1 || !item.available ? 'disabled' : ''}>-</button>
                        <span class="quantity">${item.quantity}</span>
                        <button class="quantity-btn" onclick="cart.increaseQuantity(${item.id})"
                                ${!item.available ? 'disabled' : ''}>+</button>
                    </div>
                    <div class="item-total">
                        ${(item.price * item.quantity).toLocaleString()} ₽
                    </div>
                    <button class="remove-btn" onclick="cart.removeItem(${item.id})" title="Удалить">
                        🗑️
                    </button>
                </div>
            </div>
        `).join('');
    }

    showEmptyCart() {
        if (this.elements.cartItems) this.elements.cartItems.style.display = 'none';
        if (this.elements.emptyCart) this.elements.emptyCart.style.display = 'block';
    }

    hideEmptyCart() {
        if (this.elements.cartItems) this.elements.cartItems.style.display = 'flex';
        if (this.elements.emptyCart) this.elements.emptyCart.style.display = 'none';
    }

    async increaseQuantity(itemId) {
        await this.updateQuantity(itemId, 1);
    }

    async decreaseQuantity(itemId) {
        await this.updateQuantity(itemId, -1);
    }

    async updateQuantity(itemId, change) {
        const item = this.items.find(i => i.id === itemId);
        if (!item || !item.available) return;

        const newQuantity = item.quantity + change;
        if (newQuantity < 1) return;

        this.showLoading(true);
        
        try {
            // Эмуляция API запроса
            await new Promise(resolve => setTimeout(resolve, 500));
            
            item.quantity = newQuantity;
            this.renderCart();
            this.updateSummary();
            this.saveCartToLocalStorage();
            
            // В реальном приложении:
            // await CartService.updateCartItem(itemId, newQuantity);
            
        } catch (error) {
            this.showToast(`Ошибка обновления: ${error.message}`, true);
        } finally {
            this.showLoading(false);
        }
    }

    async removeItem(itemId) {
        this.showLoading(true);
        
        try {
            // Эмуляция API запроса
            await new Promise(resolve => setTimeout(resolve, 500));
            
            this.items = this.items.filter(item => item.id !== itemId);
            this.renderCart();
            this.updateSummary();
            this.saveCartToLocalStorage();
            
            // В реальном приложении:
            // await CartService.removeFromCart(itemId);
            
            this.showToast('Товар удален из корзины');
        } catch (error) {
            this.showToast(`Ошибка удаления: ${error.message}`, true);
        } finally {
            this.showLoading(false);
        }
    }

    updateSummary() {
        if (!this.elements.subtotal || !this.elements.shipping || !this.elements.total) return;

        const subtotal = this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const shipping = subtotal > 3000 ? 0 : 500; // Бесплатная доставка от 3000₽
        const total = subtotal + shipping;

        const totalItems = this.items.reduce((sum, item) => sum + item.quantity, 0);

        this.elements.subtotal.textContent = `${subtotal.toLocaleString()} ₽`;
        this.elements.shipping.textContent = shipping === 0 ? 'Бесплатно' : `${shipping} ₽`;
        this.elements.total.textContent = `${total.toLocaleString()} ₽`;

        // Обновляем количество товаров в сводке
        const itemsTextElement = this.elements.subtotal.previousElementSibling;
        if (itemsTextElement) {
            itemsTextElement.textContent = `Товары (${totalItems})`;
        }

        // Блокируем кнопку оформления если корзина пуста
        if (this.elements.checkoutBtn) {
            this.elements.checkoutBtn.disabled = this.items.length === 0;
        }
    }

    async applyPromoCode() {
        const code = this.elements.promoCode?.value.trim();
        if (!code) {
            this.showToast('Введите промокод', true);
            return;
        }

        this.showLoading(true);
        
        try {
            // Эмуляция проверки промокода
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            if (code === 'FASHION10') {
                this.showToast('Промокод применен! Скидка 10%');
                this.applyDiscount(0.1);
            } else if (code === 'FREE500') {
                this.showToast('Промокод применен! Бесплатная доставка');
                this.applyFreeShipping();
            } else {
                this.showToast('Неверный промокод', true);
            }
        } catch (error) {
            this.showToast(`Ошибка применения промокода: ${error.message}`, true);
        } finally {
            this.showLoading(false);
        }
    }

    applyDiscount(discountRate) {
        // Применяем скидку к итоговой сумме
        const subtotal = this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const discount = Math.round(subtotal * discountRate);
        const shipping = subtotal > 3000 ? 0 : 500;
        const total = subtotal - discount + shipping;

        if (this.elements.total) {
            this.elements.total.textContent = `${total.toLocaleString()} ₽`;
            this.elements.total.innerHTML += `<div style="color: var(--success-color); font-size: 0.9em;">-${discount.toLocaleString()} ₽ скидка</div>`;
        }
    }

    applyFreeShipping() {
        const subtotal = this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const total = subtotal;

        if (this.elements.shipping) {
            this.elements.shipping.textContent = 'Бесплатно';
            this.elements.shipping.style.color = 'var(--success-color)';
        }
        if (this.elements.total) {
            this.elements.total.textContent = `${total.toLocaleString()} ₽`;
        }
    }

    async checkout() {
        if (this.items.length === 0) {
            this.showToast('Корзина пуста', true);
            return;
        }

        this.showLoading(true);
        
        try {
            // Эмуляция процесса оформления заказа
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // В реальном приложении:
            // const order = await CartService.createOrder(this.items);
            
            this.showToast('Заказ успешно оформлен!');
            
            // Очищаем корзину после успешного оформления
            this.items = [];
            this.renderCart();
            this.updateSummary();
            this.saveCartToLocalStorage();
            
            // Перенаправляем на страницу подтверждения
            setTimeout(() => {
                // window.location.href = `order-success.html?order_id=${order.id}`;
                alert('Заказ оформлен! В реальном приложении здесь будет перенаправление на страницу подтверждения.');
            }, 1000);
            
        } catch (error) {
            this.showToast(`Ошибка оформления заказа: ${error.message}`, true);
        } finally {
            this.showLoading(false);
        }
    }

    saveCartToLocalStorage() {
        try {
            localStorage.setItem('fashioneco-cart', JSON.stringify(this.items));
        } catch (error) {
            console.warn('Не удалось сохранить корзину в localStorage:', error);
        }
    }

    showLoading(show) {
        this.isLoading = show;
        if (this.elements.loadingIndicator) {
            this.elements.loadingIndicator.style.display = show ? 'block' : 'none';
        }
        
        // Блокируем кнопки при загрузке
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            if (show) {
                button.setAttribute('disabled', 'true');
            } else {
                button.removeAttribute('disabled');
            }
        });
    }

    showToast(message, isError = false) {
        if (!this.elements.toast) return;

        const toast = this.elements.toast;
        toast.textContent = message;
        toast.className = `toast ${isError ? 'error' : ''} show`;
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    // Метод для добавления товара извне
    async addItem(product) {
        const existingItem = this.items.find(item => item.id === product.id);
        
        if (existingItem) {
            await this.updateQuantity(product.id, 1);
        } else {
            this.items.push({
                ...product,
                quantity: 1
            });
            this.renderCart();
            this.updateSummary();
            this.saveCartToLocalStorage();
            this.showToast('Товар добавлен в корзину');
        }
    }

    // Получить общее количество товаров
    getTotalItems() {
        return this.items.reduce((sum, item) => sum + item.quantity, 0);
    }

    // Получить общую сумму
    getTotalPrice() {
        return this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    }
}

// Глобальная переменная для доступа к корзине
let cart;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    cart = new ShoppingCart();
    
    // Добавляем стиль для недоступных товаров
    if (!document.querySelector('#cart-styles')) {
        const style = document.createElement('style');
        style.id = 'cart-styles';
        style.textContent = `
            .item-unavailable {
                color: var(--error-color);
                font-size: 0.8em;
                font-weight: 600;
                margin-top: 4px;
            }
            .item-total {
                font-weight: 700;
                color: var(--primary-color);
                min-width: 80px;
                text-align: center;
            }
        `;
        document.head.appendChild(style);
    }
});