from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import json
from datetime import datetime
import os
import logging
from flask import Flask, request, jsonify

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Настройки
BOT_TOKEN = os.getenv('BOT_TOKEN', '8290686679:AAFt8_v9X_yzeLeOhjhlk4B-eirYOGOsT5Q')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '5127569065')
PORT = int(os.getenv('PORT', 10000))

# Создаем Flask приложение
app = Flask(__name__)

def start(update: Update, context: CallbackContext) -> None:
    """Команда /start с кнопками"""
    keyboard = [
        [InlineKeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url="https://my-tg-shop.onrender.com"))],
        [InlineKeyboardButton("👤 Мой профиль", callback_data="profile")],
        [InlineKeyboardButton("📞 Поддержка", url="https://t.me.com")]
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

    update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def handle_web_app_data(update: Update, context: CallbackContext) -> None:
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
        
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID, 
            text=order_text, 
            parse_mode='Markdown'
        )
        
        update.message.reply_text(
            "✅ *Заказ принят!*\nСпасибо за покупку! Мы свяжемся с вами soon.",
            parse_mode='Markdown'
        )
        
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
            "👋 Для открытия магазина используйте команду /start\n\n"
            "Или нажмите кнопку ниже:",
            reply_markup=reply_markup
        )

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Обработчик вебхуков от сайта"""
    try:
        data = request.json
        logger.info(f"Получен заказ: {data}")
        
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
        updater.bot.send_message(
            chat_id=ADMIN_CHAT_ID, 
            text=order_text, 
            parse_mode='Markdown'
        )
        
        return jsonify({'status': 'success'})
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервера"""
    return jsonify({'status': 'running'})

def main():
    """Основная функция запуска"""
    global updater
    
    # Создаем updater
    updater = Updater(BOT_TOKEN, use_context=True)
    
    # Добавляем обработчики
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.status_update.web_app_data, handle_web_app_data))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Запускаем polling
    updater.start_polling()
    logger.info("✅ Бот запущен и готов к работе")
    
    # Запускаем Flask сервер
    app.run(host='0.0.0.0', port=PORT, debug=False)

if __name__ == '__main__':
    main()
