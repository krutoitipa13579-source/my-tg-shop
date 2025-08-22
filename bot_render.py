from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import json
from datetime import datetime
import os
import asyncio
from aiohttp import web

# Настройки из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN', '8290686679:AAFt8_v9X_yzeLeOhjhlk4B-eirYOGOsT5Q')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '5127569065')
PORT = int(os.getenv('PORT', 10000))
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://your-render-app.onrender.com')

# Глобальные переменные
application = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start с интерактивной кнопкой"""
    shop_url = "https://my-tg-shop.onrender.com"
    
    keyboard = [
        [InlineKeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=shop_url))],
        [InlineKeyboardButton("📞 Связаться с поддержкой", url="https://t.me/your_username")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
👋 *Добро пожаловать в ABKSWAGG!*

🎉 *Магазин стильной одежды в черно-белом стиле*

✨ *Что у нас есть:*
• Модные футболки
• Стильные худи
• Удобные штаны
• Теплые куртки

🛒 *Как сделать заказ:*
1. Нажмите кнопку "Открыть магазин"
2. Выберите понравившиеся товары
3. Добавьте в корзину
4. Оформите заказ

🚚 *Бесплатная доставка по всему городу!*
⏰ *Работаем 24/7*
""".strip()

    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка данных из Web App"""
    try:
        data = json.loads(update.effective_message.web_app_data.data)
        user = update.effective_user
        
        # Форматируем текст заказа
        order_text = format_order_text(data, user)
        
        # Отправляем заказ администратору
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID, 
            text=order_text, 
            parse_mode='HTML'
        )
        
        # Отправляем подтверждение пользователю
        await update.message.reply_text(
            "✅ *Ваш заказ принят!*\n\nСпасибо за покупку! Мы свяжемся с вами в ближайшее время для подтверждения заказа.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        print(f"Ошибка обработки заказа: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при обработке заказа. Пожалуйста, попробуйте еще раз или свяжитесь с поддержкой."
        )

def format_order_text(data, user):
    """Форматирование текста заказа"""
    order_text = f"""
🛒 <b>НОВЫЙ ЗАКАЗ ИЗ МАГАЗИНА!</b>
══════════════════════════

👤 <b>Клиент:</b> {data.get('customerName', 'Не указано')}
📞 <b>Телефон:</b> <code>{data.get('customerPhone', 'Не указан')}</code>
🏠 <b>Адрес:</b> {data.get('shippingAddress', 'Не указан')}

🆔 <b>ID пользователя:</b> <code>{user.id}</code>
👤 <b>Username:</b> @{user.username if user.username else 'не указан'}
📅 <b>Дата заказа:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

📦 <b>Состав заказа:</b>
────────────────────────────
"""
    
    for i, item in enumerate(data.get('products', []), 1):
        order_text += f"""
{i}. <b>{item['name']}</b>
   • Размер: {item.get('size', 'Не выбран')}
   • Цена: {item['price']} руб.
   • Кол-во: {item.get('quantity', 1)}
   • Сумма: {item['price'] * item.get('quantity', 1)} руб.
"""
    
    order_text += f"""
────────────────────────────
💵 <b>Общая сумма: {data['totalAmount']} руб.</b>

⏰ <b>Время получения:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
"""
    return order_text

async def handle_webhook(request):
    """Обработчик вебхуков от сайта"""
    try:
        data = await request.json()
        
        # Создаем mock пользователя для веб-заказов
        web_user = type('User', (), {'id': 'WEB', 'username': 'website_user'})()
        order_text = format_order_text(data, web_user)
        
        # Отправляем заказ администратору
        await application.bot.send_message(
            chat_id=ADMIN_CHAT_ID, 
            text=order_text, 
            parse_mode='HTML'
        )
        
        return web.Response(text='OK')
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return web.Response(text='ERROR', status=500)

async def health_check(request):
    """Проверка здоровья сервера"""
    return web.Response(text='Bot is running!')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка обычных сообщений"""
    if update.message.text and not update.message.text.startswith('/'):
        await update.message.reply_text(
            "👋 Для открытия магазина используйте команду /start\n\n"
            "Или нажмите кнопку ниже:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url="https://my-tg-shop.onrender.com"))]
            ])
        )

async def main():
    """Основная функция запуска"""
    global application
    
    # Создаем приложение бота
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Настраиваем вебхук
    await application.bot.set_webhook(f"{WEBHOOK_URL}/telegram")
    
    # Создаем HTTP сервер
    app = web.Application()
    app.router.add_post('/webhook', handle_webhook)
    app.router.add_post('/telegram', lambda req: application.update_queue.put(
        Update.de_json(await req.json(), application.bot)
    ))
    app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    print(f"✅ Бот запущен на порту {PORT}")
    print(f"🌐 Webhook URL: {WEBHOOK_URL}")
    print("📞 Бот готов принимать заказы!")
    
    # Бесконечный цикл
    await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
