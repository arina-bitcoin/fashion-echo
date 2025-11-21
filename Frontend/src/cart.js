class ShoppingCart {
            constructor() {
                this.items = this.loadCart();
                this.elements = this.initializeElements();
                this.attachEventListeners();
                this.renderCart();
                this.updateSummary();
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
                    toast: document.getElementById('toast')
                };
            }

            attachEventListeners() {
                this.elements.applyPromo.addEventListener('click', () => this.applyPromoCode());
                this.elements.checkoutBtn.addEventListener('click', () => this.checkout());
                this.elements.continueShopping.addEventListener('click', () => {
                    window.location.href = '#';
                });
            }

            loadCart() {
                // В реальном приложении здесь бы была загрузка из localStorage или API
                return [
                    {
                        id: 1,
                        name: 'Платье летнее',
                        price: 1200,
                        size: 'M',
                        image: 'https://via.placeholder.com/300x300/F3E4D3/4B0505?text=Платье',
                        quantity: 1
                    },
                    {
                        id: 2,
                        name: 'Джинсы классические',
                        price: 800,
                        size: '42',
                        image: 'https://via.placeholder.com/300x300/F3E4D3/4B0505?text=Джинсы',
                        quantity: 2
                    },
                    {
                        id: 3,
                        name: 'Куртка кожаная',
                        price: 2500,
                        size: 'L',
                        image: 'https://via.placeholder.com/300x300/F3E4D3/4B0505?text=Куртка',
                        quantity: 1
                    }
                ];
            }

            renderCart() {
                if (this.items.length === 0) {
                    this.elements.cartItems.style.display = 'none';
                    this.elements.emptyCart.style.display = 'block';
                    return;
                }

                this.elements.emptyCart.style.display = 'none';
                this.elements.cartItems.style.display = 'flex';

                this.elements.cartItems.innerHTML = this.items.map(item => `
                    <div class="cart-item" data-id="${item.id}">
                        <img src="${item.image}" alt="${item.name}" class="item-image">
                        <div class="item-details">
                            <div class="item-name">${item.name}</div>
                            <div class="item-size">Размер: ${item.size}</div>
                            <div class="item-price">${item.price} ₽</div>
                        </div>
                        <div class="item-controls">
                            <div class="quantity-controls">
                                <button class="quantity-btn" onclick="cart.decreaseQuantity(${item.id})" ${item.quantity <= 1 ? 'disabled' : ''}>-</button>
                                <span class="quantity">${item.quantity}</span>
                                <button class="quantity-btn" onclick="cart.increaseQuantity(${item.id})">+</button>
                            </div>
                            <button class="remove-btn" onclick="cart.removeItem(${item.id})" title="Удалить">
                                🗑️
                            </button>
                        </div>
                    </div>
                `).join('');
            }

            updateQuantity(itemId, change) {
                const item = this.items.find(i => i.id === itemId);
                if (item) {
                    item.quantity += change;
                    if (item.quantity < 1) item.quantity = 1;
                    this.saveCart();
                    this.renderCart();
                    this.updateSummary();
                }
            }

            increaseQuantity(itemId) {
                this.updateQuantity(itemId, 1);
            }

            decreaseQuantity(itemId) {
                this.updateQuantity(itemId, -1);
            }

            removeItem(itemId) {
                this.items = this.items.filter(item => item.id !== itemId);
                this.saveCart();
                this.renderCart();
                this.updateSummary();
                this.showToast('Товар удален из корзины');
            }

            updateSummary() {
                const subtotal = this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
                const shipping = subtotal > 3000 ? 0 : 500; // Бесплатная доставка от 3000₽
                const total = subtotal + shipping;

                this.elements.subtotal.textContent = `${subtotal.toLocaleString()} ₽`;
                this.elements.shipping.textContent = shipping === 0 ? 'Бесплатно' : `${shipping} ₽`;
                this.elements.total.textContent = `${total.toLocaleString()} ₽`;

                // Обновляем количество товаров в сводке
                const totalItems = this.items.reduce((sum, item) => sum + item.quantity, 0);
                this.elements.subtotal.previousElementSibling.textContent = `Товары (${totalItems})`;
            }

            applyPromoCode() {
                const code = this.elements.promoCode.value.trim();
                if (code === 'FASHION10') {
                    this.showToast('Промокод применен! Скидка 10%');
                    // Здесь была бы логика применения скидки
                } else if (code) {
                    this.showToast('Неверный промокод', true);
                }
            }

            checkout() {
                if (this.items.length === 0) {
                    this.showToast('Корзина пуста', true);
                    return;
                }

                this.showToast('Переход к оформлению заказа...');
                // В реальном приложении здесь был бы переход на страницу оформления
                setTimeout(() => {
                    alert('Оформление заказа! В реальном приложении здесь была бы страница оформления.');
                }, 1000);
            }

            saveCart() {
                // В реальном приложении здесь бы было сохранение в localStorage
                localStorage.setItem('fashioneco-cart', JSON.stringify(this.items));
            }

            showToast(message, isError = false) {
                const toast = this.elements.toast;
                toast.textContent = message;
                toast.className = `toast ${isError ? 'error' : ''} show`;
                
                setTimeout(() => {
                    toast.classList.remove('show');
                }, 3000);
            }
        }

        // Инициализация корзины при загрузке страницы
        let cart;
        document.addEventListener('DOMContentLoaded', () => {
            cart = new ShoppingCart();
        });