from flask import Flask, request

app = Flask(__name__)
CONFIRMATION_TOKEN = "af11f5df"  # Замените на ваш токен!

@app.route('/callback', methods=['POST'])
def callback():
    data = request.json
    if data.get('type') == 'confirmation':
        return CONFIRMATION_TOKEN  # Возвращаем строку!
    return 'ok'  # Для других запросов

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Важно: host='0.0.0.0'!

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Токен вашего бота (замените на свой)
TOKEN = "7746859733:AAFxsCqRDCAXi2iy3ofZ-v20WYaiXoegPJg"

# Обработчик команды /start
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(f"Привет, {user.first_name}! Я простой бот. Напиши мне что-нибудь, и я повторю.")

# Обработчик текстовых сообщений
def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)

def main() -> None:
    # Создаем объект Updater и передаем ему токен бота
    updater = Updater(TOKEN)

    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Регистрируем обработчики команд и сообщений
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()
    print("Бот запущен...")

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
