import os
import json
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# 🔹 Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🔹 Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

# ---------- Команды ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие и кнопки"""
    keyboard = [
        [InlineKeyboardButton("🛍️ Магазин", web_app=WebAppInfo(url="https://my-tg-shop.onrender.com"))],
        [InlineKeyboardButton("👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton("📞 Поддержка", url="https://t.me/your_support")]
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

🛒 Чтобы начать покупки — нажмите «Магазин» ниже 👇
""".strip()

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка заказов из WebApp"""
    try:
        data = json.loads(update.effective_message.web_app_data.data)
        user = update.effective_user

        order_text = f"""
🛒 НОВЫЙ ЗАКАЗ!
═══════════════════════
👤 Клиент: {data.get('customerName', 'Не указано')}
📞 Телефон: {data.get('customerPhone', 'Не указан')}
🏠 Адрес: {data.get('shippingAddress', 'Не указан')}

🆔 UserID: {user.id}
👤 Username: @{user.username if user.username else 'не указан'}
📅 Время заказа: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

📦 Товары:
────────────────────────
"""
        for i, item in enumerate(data.get("products", []), 1):
            order_text += f"""
{i}. {item['name']}
   • Размер: {item.get('size', 'Не выбран')}
   • Цена: {item['price']} руб.
   • Кол-во: {item.get('quantity', 1)}
   • Сумма: {item['price'] * item.get('quantity', 1)} руб.
"""

        order_text += f"""
────────────────────────
💵 ИТОГО: {data['totalAmount']} руб.
⏰ Получение: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
"""

        # Отправляем админу
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=order_text)

        # Подтверждаем клиенту
        await update.message.reply_text("✅ Заказ принят! Спасибо за покупку!")

    except Exception as e:
        logger.error(f"Ошибка обработки заказа: {e}")
        await update.message.reply_text("❌ Ошибка при обработке заказа.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ответ на любые текстовые сообщения"""
    if update.message.text and not update.message.text.startswith("/"):
        keyboard = [
            [InlineKeyboardButton("🛍️ Магазин", web_app=WebAppInfo(url="https://my-tg-shop.onrender.com"))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "👋 Чтобы открыть магазин, нажмите кнопку ниже:",
            reply_markup=reply_markup
        )

# ---------- Основная функция ----------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("✅ Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()
