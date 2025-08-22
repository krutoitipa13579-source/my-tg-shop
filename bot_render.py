import os
import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Настройки
BOT_TOKEN = os.getenv('BOT_TOKEN', '8290686679:AAFt8_v9X_yzeLeOhjhlk4B-eirYOGOsT5Q')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '5127569065')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start с кнопками"""
    keyboard = [
        [InlineKeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url="https://my-tg-shop.onrender.com"))],
        [InlineKeyboardButton("👤 Мой профиль", callback_data="profile")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
👋 Добро пожаловать в ABKSWAGA!

🎉 Магазин стильной одежды

✨ Преимущества:
• Быстрая доставка
• Качественные материалы
• Стильные модели
• Доступные цены

🛒 Чтобы начать покупки:
Нажмите кнопку «Открыть магазин»
""".strip()

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка заказов из Web App"""
    try:
        data = update.message.web_app_data.data
        user = update.effective_user
        
        order_text = f"""
🛒 НОВЫЙ ЗАКАЗ ИЗ WEB APP!
══════════════════════════

👤 Клиент: {data.get('customerName', 'Не указано')}
📞 Телефон: {data.get('customerPhone', 'Не указан')}
🏠 Адрес: {data.get('shippingAddress', 'Не указан')}

🆔 ID: {user.id}
👤 Username: @{user.username if user.username else 'не указан'}
📅 Дата: {time.strftime('%d.%m.%Y %H:%M:%S')}

📦 Заказ:
────────────────────────────
"""
        
        for i, item in enumerate(data.get('products', []), 1):
            order_text += f"""
{i}. {item['name']}
   • Размер: {item.get('size', 'Не выбран')}
   • Цена: {item['price']} руб.
   • Кол-во: {item.get('quantity', 1)}
   • Сумма: {item['price'] * item.get('quantity', 1)} руб.
"""
        
        order_text += f"""
────────────────────────────
💵 Итого: {data.get('totalAmount', 0)} руб.
⏰ Время: {time.strftime('%d.%m.%Y %H:%M:%S')}
"""
        
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=order_text)
        await update.message.reply_text("✅ Заказ принят! Спасибо!")
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("❌ Ошибка при обработке заказа.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка обычных сообщений"""
    if update.message.text and not update.message.text.startswith('/'):
        keyboard = [
            [InlineKeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url="https://my-tg-shop.onrender.com"))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "👋 Используйте /start для открытия магазина",
            reply_markup=reply_markup
        )

def main():
    """Основная функция запуска"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()
    logger.info("✅ Бот запущен")

if __name__ == '__main__':
    main()
