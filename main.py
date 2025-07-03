from flask import Flask, request, Response
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import requests
from telegram import Bot, InputFile
import logging

app = Flask(__name__)
CONFIRMATION_TOKEN = "af11f5df"  # Токен который хочет Вэка

@app.route('/callback', methods=['POST'])
def callback():
    data = request.json
    if data.get('type') == 'confirmation':
        return CONFIRMATION_TOKEN
    return 'ok'  # Для других запросов

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


# Далее
VK_TOKEN = "vk1.a.Z1IGf-BPMZUdGASE3_B6B8aX3nfuPr9CnVHfo5kMTMy8g_beismhyI1vr2z-v0ucXQUaDrqzdC9dSMEUN1ZgL-5gmRc72enBln_ZxUSWqQHO5BuCrhtPOFQkJvLOUCR12P_XFLyLblkSRIInpEMmCkQehyulmr6n1YyT71DH8wc4Pw0rQORt8FCiqQQFo6GxgqGx3ROmum7EKNhLArvTQA"
VK_GROUP_ID = "231360270"
# Ссылка на группу вк где бот: https://vk.com/club231360270
TG_TOKEN = "7746859733:AAFxsCqRDCAXi2iy3ofZ-v20WYaiXoegPJg"


# Настройка логирования для отслеживания работы бота
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CONFIRMATION_TOKEN = "af11f5df" # Токен для подтверждения сервера в настройках Callback API

# Инициализация клиентов для работы с API
vk_session = vk_api.VkApi(token=VK_TOKEN) # Сессия ВКонтакте
tg_bot = Bot(token=TG_TOKEN) # Клиент Telegram бота

@app.route('/callback', methods=['POST'])
def callback():
    """Обработчик запросов от Callback API ВКонтакте"""
    data = request.json
    if data.get('type') == 'confirmation':
        return Response(CONFIRMATION_TOKEN, mimetype='text/plain')
    return 'ok'

def download_audio(url):
    """Загрузка аудиофайла по URL"""
    return requests.get(url, stream=True).content

def send_welcome(user_id):
    """Отправка приветственного сообщения новому пользователю"""
    vk_session.method("messages.send", {
        "user_id": user_id,
        "message": "Привет! Отправь мне аудиозапись, и я перешлю её в Telegram.",
        "random_id": 0
    })

def main():
    """Основная логика работы бота"""
    try:
        longpoll = VkBotLongPoll(vk_session, VK_GROUP_ID)
        
        # Главный цикл обработки событий
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                msg = event.object.message
                user_id = msg["from_id"]
                
                # Обработка команд
                if msg.get("text", "").lower() in ('привет', 'начать', 'start'):
                    send_welcome(user_id)
                
                # Обработка вложений
                if "attachments" in msg:
                    for att in msg["attachments"]:
                        if att["type"] == "audio":
                            try:
                                # Получаем данные аудиозаписи
                                audio_url = att["audio"]["url"]
                                title = f"{att['audio']['artist']} - {att['audio']['title']}"
                                
                                # Загружаем и отправляем аудио
                                audio_data = download_audio(audio_url)
                                tg_bot.send_audio(
                                    chat_id=user_id,
                                    audio=InputFile(audio_data, filename=f"{title}.mp3"),
                                    title=title
                                )
                                
                                # Подтверждение отправки
                                vk_session.method("messages.send", {
                                    "user_id": user_id,
                                    "message": "Аудио отправлено в Telegram!",
                                    "random_id": 0
                                })
                                
                            except Exception as e:
                                logger.error(f"Ошибка: {e}")
                                vk_session.method("messages.send", {
                                    "user_id": user_id,
                                    "message": "Не удалось обработать аудио",
                                    "random_id": 0
                                })
                                
    except vk_api.exceptions.ApiError as e:
        logger.error(f"Ошибка VK API: {e}")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
