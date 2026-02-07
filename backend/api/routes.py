from flask import Blueprint, request, jsonify
import cv2
import base64
import numpy as np
import time

from backend.detection.detector import PersonDetector
from backend.services.telegram_service import TelegramService
from backend.services.alert_service import AlertService

api = Blueprint("api", __name__)

detector = PersonDetector()
telegram = TelegramService()
alerts = AlertService()

# Variables globales para controlar cooldown de alertas
last_alert_time = 0
ALERT_COOLDOWN = 30  # segundos

@api.route("/api/v1/detect", methods=["POST"])
def detect():
    
    global last_alert_time
    
    # 1. Verificar que venga imagen
    file = request.files.get("image")
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files["image"]

    # 2. Leer imagen como OpenCV
    image_bytes = file.read()
    if not image_bytes:
        return jsonify({"error": "Empty image"}), 400
    
    np_img = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "Invalid image"}), 400

    # 3. Detección
    detections = detector.detect(frame)

    # 4. Enviar alerta a Telegram si hay detecciones
    alert_sent = False
    now = time.time()
    if len(detections) > 0 and now - last_alert_time > ALERT_COOLDOWN:
        telegram.send_alert(frame, detections)
        last_alert_time = now
        alert_sent = True

    # 5. Respuesta
    return jsonify({
        "detections": detections,
        "alert_sent": alert_sent,
        "backend_status": "ONLINE"
    })