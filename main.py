import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import requests
from telegram import Bot, InputFile

# Настройки
VK_TOKEN = "vk1.a.Z1IGf-BPMZUdGASE3_B6B8aX3nfuPr9CnVHfo5kMTMy8g_beismhyI1vr2z-v0ucXQUaDrqzdC9dSMEUN1ZgL-5gmRc72enBln_ZxUSWqQHO5BuCrhtPOFQkJvLOUCR12P_XFLyLblkSRIInpEMmCkQehyulmr6n1YyT71DH8wc4Pw0rQORt8FCiqQQFo6GxgqGx3ROmum7EKNhLArvTQA"
VK_GROUP_ID = "231360270"
TG_TOKEN = "7746859733:AAFxsCqRDCAXi2iy3ofZ-v20WYaiXoegPJg"

# Инициализация ВК-бота
vk_session = vk_api.VkApi(token=VK_TOKEN)
longpoll = VkBotLongPoll(vk_session, VK_GROUP_ID)

# Инициализация Telegram-бота
tg_bot = Bot(token=TG_TOKEN)

def download_audio(url):
    return requests.get(url).content

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        msg = event.object.message
        user_id = msg["from_id"]
        
        if "attachments" in msg:
            for att in msg["attachments"]:
                if att["type"] == "audio":
                    audio_url = att["audio"]["url"]
                    title = f"{att['audio']['artist']} - {att['audio']['title']}"
                    
                    # Скачиваем и отправляем в Telegram
                    audio_data = download_audio(audio_url)
                    tg_bot.send_audio(
                        chat_id=user_id,  # или любой другой chat_id
                        audio=InputFile(audio_data, filename=f"{title}.mp3"),
                        title=title
                    )
                    vk_session.method("messages.send", {
                        "user_id": user_id,
                        "message": "🎵 Аудио отправлено в Telegram!",
                        "random_id": 0
                    })