from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def send_image(image_path: str, caption: str = ""):
    with open(image_path, "rb") as img:
        await bot.send_photo(
            chat_id=TELEGRAM_CHAT_ID,
            photo=img,
            caption=caption
        )