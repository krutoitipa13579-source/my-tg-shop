<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Магазин одежды</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: Arial; background: #f5f5f5; padding: 20px; }
        .product { background: white; border-radius: 10px; padding: 15px; margin: 10px 0; }
        .product img { width: 100%; border-radius: 8px; margin-bottom: 10px; }
        .price { color: #e91e63; font-weight: bold; }
        .sizes { display: flex; gap: 5px; margin: 10px 0; }
        .size-btn { padding: 8px; border: 1px solid #ddd; border-radius: 5px; background: #f9f9f9; }
        .size-btn.selected { background: #e91e63; color: white; }
        .add-to-cart { background: #4CAF50; color: white; border: none; padding: 10px; border-radius: 5px; width: 100%; }
        .cart { position: fixed; bottom: 20px; right: 20px; background: #ff5722; color: white; padding: 15px; border-radius: 50%; }
    </style>
</head>
<body>
    <h2>👕 Магазин одежды</h2>
    
    <div class="product">
        <img src="https://via.placeholder.com/300x300?text=Футболка" alt="Футболка">
        <h3>Футболка оверсайз</h3>
        <div class="price">1 999 руб.</div>
        <div class="sizes">
            <button class="size-btn" onclick="selectSize(this, 'S')">S</button>
            <button class="size-btn" onclick="selectSize(this, 'M')">M</button>
            <button class="size-btn" onclick="selectSize(this, 'L')">L</button>
        </div>
        <button class="add-to-cart" onclick="addToCart('Футболка оверсайз', 1999)">Добавить в корзину</button>
    </div>

    <div class="product">
        <img src="https://via.placeholder.com/300x300?text=Худи" alt="Худи">
        <h3>Худи с капюшоном</h3>
        <div class="price">4 499 руб.</div>
        <div class="sizes">
            <button class="size-btn" onclick="selectSize(this, 'M')">M</button>
            <button class="size-btn" onclick="selectSize(this, 'L')">L</button>
        </div>
        <button class="add-to-cart" onclick="addToCart('Худи с капюшоном', 4499)">Добавить в корзину</button>
    </div>

    <div class="cart" onclick="showCart()">🛒 <span id="cart-count">0</span></div>

    <script>
        let cart = [];
        let selectedSize = '';

        function selectSize(btn, size) {
            document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            selectedSize = size;
        }

        function addToCart(name, price) {
            if (!selectedSize) return alert('Выберите размер!');
            
            cart.push({ name, price, size: selectedSize, quantity: 1 });
            document.getElementById('cart-count').textContent = cart.length;
            alert('Добавлено в корзину!');
            selectedSize = '';
            document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('selected'));
        }

        function showCart() {
            if (cart.length === 0) return alert('Корзина пуста!');
            
            let total = cart.reduce((sum, item) => sum + item.price, 0);
            let message = '🛒 Ваша корзина:\n\n';
            cart.forEach(item => message += `• ${item.name} (${item.size}) - ${item.price} руб.\n`);
            message += `\n💵 Итого: ${total} руб.\n\nОформить заказ?`;

            if (confirm(message)) {
                const name = prompt('Ваше имя:');
                const phone = prompt('Ваш телефон:');
                const address = prompt('Адрес доставки:');
                
                if (name && phone && address) {
                    const orderData = { products: cart, totalAmount: total, customerName: name, customerPhone: phone, shippingAddress: address };
                    Telegram.WebApp.sendData(JSON.stringify(orderData));
                    Telegram.WebApp.close();
                }
            }
        }
    </script>
</body>
</html>
