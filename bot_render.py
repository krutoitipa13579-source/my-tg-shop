from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import json
from datetime import datetime
import os
import asyncio
from aiohttp import web

# Настройки
BOT_TOKEN = os.getenv('BOT_TOKEN', '8290686679:AAFt8_v9X_yzeLeOhjhlk4B-eirYOGOsT5Q')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '5127569065')
PORT = int(os.getenv('PORT', 10000))

application = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start с кнопками"""
    keyboard = [
        [InlineKeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url="https://my-tg-shop.onrender.com"))],
        [InlineKeyboardButton("👤 Мой профиль", callback_data="profile")],
        [InlineKeyboardButton("📞 Поддержка", url="https://t.me/your_username")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
👋 *Добро пожаловать в ABKSWAGA!*

🎉 *Магазин стильной одежды*

✨ *Преимущества:*
• Быстрая доставка
• Качественные материалы
• Стильные модели
• Доступные цены

🛒 *Чтобы начать покупки:*
Нажмите кнопку «Открыть магазин» ниже 👇
""".strip()

    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка заказов из Web App"""
    try:
        data = json.loads(update.effective_message.web_app_data.data)
        user = update.effective_user
        
        order_text = f"""
🛒 *НОВЫЙ ЗАКАЗ ИЗ WEB APP!*
══════════════════════════

👤 *Клиент:* {data.get('customerName', 'Не указано')}
📞 *Телефон:* `{data.get('customerPhone', 'Не указан')}`
🏠 *Адрес:* {data.get('shippingAddress', 'Не указан')}

🆔 *ID пользователя:* `{user.id}`
👤 *Username:* @{user.username if user.username else 'не указан'}
📅 *Дата заказа:* {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

📦 *Состав заказа:*
────────────────────────────
"""
        
        for i, item in enumerate(data.get('products', []), 1):
            order_text += f"""
{i}. *{item['name']}*
   • Размер: {item.get('size', 'Не выбран')}
   • Цена: {item['price']} руб.
   • Кол-во: {item.get('quantity', 1)}
   • Сумма: {item['price'] * item.get('quantity', 1)} руб.
"""
        
        order_text += f"""
────────────────────────────
💵 *Общая сумма: {data['totalAmount']} руб.*

⏰ *Время получения:* {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
"""
        
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID, 
            text=order_text, 
            parse_mode='Markdown'
        )
        
        await update.message.reply_text(
            "✅ *Заказ принят!*\nСпасибо за покупку! Мы свяжемся с вами soon.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        print(f"Ошибка обработки заказа: {e}")
        await update.message.reply_text("❌ Ошибка при обработке заказа.")

async def handle_webhook(request):
    """Обработчик вебхуков от сайта"""
    try:
        data = await request.json()
        print(f"Получен заказ: {data}")
        
        # Форматируем текст заказа
        order_text = f"""
🛒 *ЗАКАЗ ИЗ САЙТА!*
══════════════════════════

👤 *Клиент:* {data.get('customerName', 'Не указано')}
📞 *Телефон:* `{data.get('customerPhone', 'Не указан')}`
🏠 *Адрес:* {data.get('shippingAddress', 'Не указан')}
🏪 *Магазин:* {data.get('shopName', 'ABKSWAGA')}

📦 *Состав заказа:*
────────────────────────────
"""
        
        for i, item in enumerate(data.get('products', []), 1):
            order_text += f"""
{i}. *{item['name']}*
   • Размер: {item.get('size', 'Не выбран')}
   • Цена: {item['price']} руб.
   • Кол-во: {item.get('quantity', 1)}
   • Сумма: {item['price'] * item.get('quantity', 1)} руб.
"""
        
        order_text += f"""
────────────────────────────
💵 *Общая сумма: {data['totalAmount']} руб.*

⏰ *Время получения:* {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
"""
        
        # Отправляем заказ администратору
        await application.bot.send_message(
            chat_id=ADMIN_CHAT_ID, 
            text=order_text, 
            parse_mode='Markdown'
        )
        
        return web.Response(text='Order processed successfully!')
            
    except Exception as e:
        print(f"Webhook error: {e}")
        return web.Response(text='ERROR', status=500)

async def health_check(request):
    """Проверка здоровья сервера"""
    return web.Response(text='Bot is running!')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка обычных сообщений"""
    if update.message.text and not update.message.text.startswith('/'):
        keyboard = [
            [InlineKeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url="https://my-tg-shop.onrender.com"))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "👋 Для открытия магазина используйте команду /start\n\n"
            "Или нажмите кнопку ниже:",
            reply_markup=reply_markup
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка callback-запросов"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "profile":
        await query.edit_message_text(
            "👤 *Ваш профиль*\n\n"
            f"🆔 ID: `{query.from_user.id}`\n"
            f"👤 Имя: {query.from_user.first_name}\n"
            f"📧 Username: @{query.from_user.username if query.from_user.username else 'не указан'}\n\n"
            "Для заказа товаров нажмите кнопку ниже:",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url="https://my-tg-shop.onrender.com"))]
            ])
        )

async def telegram_webhook(request):
    """Обработчик вебхука от Telegram"""
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return web.Response(text='OK')
    except Exception as e:
        print(f"Telegram webhook error: {e}")
        return web.Response(text='ERROR', status=500)

async def main():
    """Основная функция запуска"""
    global application
    
    # Создаем приложение бота
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    await application.initialize()
    await application.start()
    
    print("✅ Бот инициализирован")
    
    # Создаем HTTP сервер
    app = web.Application()
    app.router.add_post('/webhook', handle_webhook)
    app.router.add_post('/telegram', telegram_webhook)
    app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    print(f"✅ Сервер запущен на порту {PORT}")
    print("🌐 Webhook: /webhook")
    print("📞 Бот готов принимать заказы!")
    
    # Бесконечный цикл
    await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
