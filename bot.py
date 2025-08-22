from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import json
from datetime import datetime
import os

# Берем токен и ID из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN', '8290686679:AAFt8_v9X_yzeLeOhjhlk4B-eirYOGOsT5Q')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', '5127569065'))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    shop_url = "https://krutoitipa13579-source.github.io/my-tg-shop/"
    
    keyboard = [[
        InlineKeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=shop_url))
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        '👋 Добро пожаловать в FashionStore!\n\n'
        'Нажмите кнопку ниже, чтобы открыть каталог стильной одежды с корзиной и выбором размеров.',
        reply_markup=reply_markup
    )

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        data = json.loads(update.effective_message.web_app_data.data)
        user = update.effective_user
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        
        # Формируем ДЕТАЛЬНЫЙ текст заказа
        order_text = "🛒 *НОВЫЙ ЗАКАЗ!*\n"
        order_text += "══════════════════════════\n\n"
        
        order_text += f"👤 *Клиент:* {data.get('customerName', 'Не указано')}\n"
        order_text += f"📞 *Телефон:* `{data.get('customerPhone', 'Не указан')}`\n"
        order_text += f"🏠 *Адрес:* {data.get('shippingAddress', 'Не указан')}\n\n"
        
        order_text += f"🆔 *ID пользователя:* `{user.id}`\n"
        order_text += f"👤 *Username:* @{user.username if user.username else 'не указан'}\n"
        order_text += f"📅 *Дата заказа:* {current_time}\n\n"
        
        order_text += "📦 *Состав заказа:*\n"
        order_text += "────────────────────────────\n"
        
        for i, item in enumerate(data.get('products', []), 1):
            order_text += f"{i}. *{item['name']}*\n"
            order_text += f"   • Размер: {item.get('size', 'Не выбран')}\n"
            order_text += f"   • Цена: {item['price']} руб.\n"
            order_text += f"   • Кол-во: {item.get('quantity', 1)}\n"
            order_text += f"   • Сумма: {item['price'] * item.get('quantity', 1)} руб.\n\n"
        
        order_text += "────────────────────────────\n"
        order_text += f"💵 *Общая сумма: {data['totalAmount']} руб.*\n\n"
        
        order_text += "⏰ *Рекомендуемое время доставки:*\n"
        order_text += "Завтра, 10:00-18:00 (уточнить у клиента)\n\n"
        
        order_text += "🔔 *Действия:*\n"
        order_text += "1. Позвонить клиенту для подтверждения\n"
        order_text += "2. Уточнить время доставки\n"
        order_text += "3. Подготовить заказ к отправку"

        # Отправляем заказ себе в личку
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID, 
            text=order_text, 
            parse_mode='Markdown'
        )
        
        # Отправляем подтверждение пользователю
        await update.message.reply_text(
            "✅ *Ваш заказ принят!*\n\n"
            "Спасибо за покупку! Мы свяжемся с вами в течение 15 минут для подтверждения заказа.\n\n"
            "📞 *Наш телефон:* +7 (999) 123-45-67\n"
            "⏰ *Время работы:* 9:00-21:00",
            parse_mode='Markdown'
        )
        
        # Дополнительное уведомление для админа
        alert_text = f"🚨 *СРОЧНО! НОВЫЙ ЗАКАЗ!*\n\n"
        alert_text += f"Клиент: {data.get('customerName', 'Не указано')}\n"
        alert_text += f"Телефон: {data.get('customerPhone', 'Не указан')}\n"
        alert_text += f"Сумма: {data['totalAmount']} руб.\n\n"
        alert_text += f"*Срочно перезвонить!*"
        
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID, 
            text=alert_text, 
            parse_mode='Markdown'
        )
        
    except Exception as e:
        print(f"Ошибка: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обработке заказа. Пожалуйста, попробуйте еще раз.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    
    print("🎉 Бот запущен! Ожидаем сообщения...")
    print("📞 Заказы будут приходить сюда с полной информацией!")
    application.run_polling()

if __name__ == '__main__':
    main()
