import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from bot_sender import BOT_TOKEN
from pose_image_mediapipe import run_pose_image
from pose_video_mediapipe import run_pose_video

UPLOADS_DIR = "telegram_bot/uploads"
OUTPUTS_DIR = "telegram_bot/outputs"

IMG_IN = os.path.join(UPLOADS_DIR, "input.jpg")
VID_IN = os.path.join(UPLOADS_DIR, "input.mp4")

IMG_OUT = os.path.join(OUTPUTS_DIR, "pose_img.jpg")
VID_OUT = os.path.join(OUTPUTS_DIR, "pose_video.mp4")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        " UPS Vision Bot\n"
        " Envíame imagen o video para detectar postura humana."
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Procesando imagen...")

    photo = update.message.photo[-1]
    file = await photo.get_file()
    await file.download_to_drive(IMG_IN)

    run_pose_image(IMG_IN, IMG_OUT)

    with open(IMG_OUT, "rb") as f:
        await update.message.reply_photo(photo=f, caption=" Pose detectada (imagen)")


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(" Procesando video...")

    if update.message.video:
        file = await update.message.video.get_file()
    elif update.message.document:
        file = await update.message.document.get_file()
    else:
        await update.message.reply_text(" No es video válido")
        return

    await file.download_to_drive(VID_IN)

    run_pose_video(VID_IN, VID_OUT)

    with open(VID_OUT, "rb") as f:
        await update.message.reply_video(video=f, caption=" Pose detectada (video)")


def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL, handle_video))

    print(" Bot Telegram corriendo...")
    app.run_polling()


if __name__ == "__main__":
    main()
