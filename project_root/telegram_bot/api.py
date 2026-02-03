from flask import Flask, request, jsonify
import os
import time
import requests

from pose_image_mediapipe import run_pose_image
from pose_video_mediapipe import run_pose_video

# ==================== CONFIG ====================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not BOT_TOKEN:
    raise RuntimeError(" TELEGRAM_BOT_TOKEN no definido")

if not CHAT_ID:
    raise RuntimeError(" TELEGRAM_CHAT_ID no definido")

UPLOAD_DIR = "telegram_bot/uploads"
OUTPUT_DIR = "telegram_bot/outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

IMG_IN = os.path.join(UPLOAD_DIR, "input.png")
VID_IN = os.path.join(UPLOAD_DIR, "input.mp4")

IMG_OUT = os.path.join(OUTPUT_DIR, "pose_img.jpg")
VID_OUT = os.path.join(OUTPUT_DIR, "pose_video.mp4")

app = Flask(__name__)

# ==================== TELEGRAM ====================

def send_photo(path, caption):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    with open(path, "rb") as f:
        r = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "caption": caption
            },
            files={"photo": f},
            timeout=30
        )

    if r.status_code != 200:
        print(" Error enviando foto:", r.text)
    else:
        print(" Imagen enviada a Telegram")


def send_video(path, caption):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"

    with open(path, "rb") as f:
        r = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "caption": caption
            },
            files={"video": f},
            timeout=60
        )

    if r.status_code != 200:
        print(" Error enviando video:", r.text)
    else:
        print(" Video enviado a Telegram")


# ==================== API ====================

@app.route("/upload", methods=["POST"])
def upload():

    if "image" not in request.files or "video" not in request.files:
        return jsonify({"error": "Faltan archivos"}), 400

    image = request.files["image"]
    video = request.files["video"]

    image.save(IMG_IN)
    video.save(VID_IN)

    fps = request.form.get("fps", "0")
    timestamp = request.form.get("timestamp", str(time.time()))
    confidence = request.form.get("confidence", "0")

    print("\n Evidencia recibida por API")
    print(" Timestamp:", timestamp)
    print(" FPS:", fps)
    print(" Confidence:", confidence)

    # ---------- POSE IMAGE ----------
    print(" Procesando pose imagen...")
    run_pose_image(IMG_IN, IMG_OUT)

    # ---------- POSE VIDEO ----------
    print(" Procesando pose video...")
    run_pose_video(VID_IN, VID_OUT)

    # ---------- ENVIAR A TELEGRAM ----------
    send_photo(
        IMG_OUT,
        f" Pose detectada\nFPS: {fps}\nConfianza: {confidence}"
    )

    send_video(
        VID_OUT,
        f" Video con pose\nFPS: {fps}"
    )

    print(" Evidencia enviada a Telegram")

    return jsonify({"status": "ok"})


# ==================== MAIN ====================

if __name__ == "__main__":
    print(" API corriendo en http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)
