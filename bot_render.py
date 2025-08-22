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

# Глобальные переменные
app = None
bot_app = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    shop_url = "https://my-tg-shop.onrender.com"
    
    keyboard = [[
        InlineKeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=shop_url))
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        '👋 Добро пожаловать в ABKSWAGG!\n\n'
        'Нажмите кнопку ниже, чтобы открыть наш магазин стильной одежды.',
        reply_markup=reply_markup
    )

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        data = json.loads(update.effective_message.web_app_data.data)
        await process_order(data, update.effective_user)
        await update.message.reply_text("✅ Заказ принят! Спасибо за покупку!")
    except Exception as e:
        print(f"Ошибка: {e}")
        await update.message.reply_text("❌ Ошибка обработки заказа.")

async def process_order(data, user):
    order_text = format_order_text(data, user)
    await bot_app.bot.send_message(chat_id=ADMIN_CHAT_ID, text=order_text, parse_mode='HTML')

def format_order_text(data, user):
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
    try:
        data = await request.json()
        await process_order(data, type('User', (), {'id': 'WEB', 'username': 'website'}))
        return web.Response(text='OK')
    except Exception as e:
        print(f"Webhook error: {e}")
        return web.Response(text='ERROR', status=500)

async def health_check(request):
    return web.Response(text='Bot is running!')

async def main():
    global bot_app, app
    
    # Инициализация бота
    bot_app = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    
    # Запускаем бота
    await bot_app.initialize()
    await bot_app.start()
    
    # Создаем HTTP сервер
    app = web.Application()
    app.router.add_post('/webhook', handle_webhook)
    app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    print(f"✅ Бот запущен на порту {PORT}")
    print("🌐 Webhook: /webhook")
    
    # Бесконечный цикл
    await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
