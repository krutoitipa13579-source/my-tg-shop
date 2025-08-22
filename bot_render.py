from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import json
from datetime import datetime
import os
import logging
import time

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Настройки
BOT_TOKEN = os.getenv('BOT_TOKEN', '8290686679:AAFt8_v9X_yzeLeOhjhlk4B-eirYOGOsT5Q')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '5127569065')

def start(update: Update, context: CallbackContext) -> None:
    """Команда /start с кнопками"""
    keyboard = [
        [InlineKeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url="https://my-tg-shop.onrender.com"))],
        [InlineKeyboardButton("👤 Мой профиль", callback_data="profile")],
        [InlineKeyboardButton("📞 Поддержка", url="https://t.me.com")]
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
Нажмите кнопку «Открыть магазин» ниже 👇
""".strip()

    update.message.reply_text(welcome_text, reply_markup=reply_markup)

def handle_web_app_data(update: Update, context: CallbackContext) -> None:
    """Обработка заказов из Web App"""
    try:
        data = json.loads(update.effective_message.web_app_data.data)
        user = update.effective_user
        
        order_text = f"""
🛒 НОВЫЙ ЗАКАЗ ИЗ WEB APP!
══════════════════════════

👤 Клиент: {data.get('customerName', 'Не указано')}
📞 Телефон: {data.get('customerPhone', 'Не указан')}
🏠 Адрес: {data.get('shippingAddress', 'Не указан')}

🆔 ID пользователя: {user.id}
👤 Username: @{user.username if user.username else 'не указан'}
📅 Дата заказа: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

📦 Состав заказа:
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
💵 Общая сумма: {data['totalAmount']} руб.

⏰ Время получения: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
"""
        
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=order_text)
        update.message.reply_text("✅ Заказ принят! Спасибо за покупку!")
        
    except Exception as e:
        logger.error(f"Ошибка обработки заказа: {e}")
        update.message.reply_text("❌ Ошибка при обработке заказа.")

def handle_message(update: Update, context: CallbackContext):
    """Обработка обычных сообщений"""
    if update.message.text and not update.message.text.startswith('/'):
        keyboard = [
            [InlineKeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url="https://my-tg-shop.onrender.com"))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            "👋 Для открытия магазина используйте команду /start\n\nИли нажмите кнопку ниже:",
            reply_markup=reply_markup
        )

def error(update: Update, context: CallbackContext):
    """Обработчик ошибок"""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Основная функция запуска"""
    updater = Updater(BOT_TOKEN, use_context=True)
    
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.status_update.web_app_data, handle_web_app_data))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_error_handler(error)
    
    updater.start_polling()
    logger.info("✅ Бот запущен и готов к работе")
    
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()
