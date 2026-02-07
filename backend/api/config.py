import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads")
OUTPUT_DIR = os.path.join(BACKEND_DIR, "outputs")

IMG_IN = os.path.join(UPLOAD_DIR, "input.png")
VID_IN = os.path.join(UPLOAD_DIR, "input.mp4")

IMG_OUT = os.path.join(OUTPUT_DIR, "pose_img.jpg")
VID_OUT = os.path.join(OUTPUT_DIR, "pose_video.mp4")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def ensure_dirs() -> None:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def validate_env(require_chat_id: bool = True) -> None:
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN no definido")
    if require_chat_id and not CHAT_ID:
        raise RuntimeError("TELEGRAM_CHAT_ID no definido")
