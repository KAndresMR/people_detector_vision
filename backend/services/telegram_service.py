import requests
import os
from datetime import datetime
import cv2
import io

class TelegramService:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.api_url_photo = f"https://api.telegram.org/bot{self.token}/sendPhoto"
        self.api_url_text = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_alert(self, frame, detections, pose_frame=None):
        """
        Envía alerta al usuario de Telegram.
        Si pose_frame se provee, envía también la imagen con keypoints.
        """
        import io
        if not self.token or not self.chat_id:
            print("[Telegram] Token o Chat ID no configurados")
            return False
        if len(detections) == 0:
            print("[Telegram] No hay detecciones para enviar")
            return False

        success = True
        # Convertir imagen original
        _, buffer = cv2.imencode(".png", frame)
        photo_bytes = io.BytesIO(buffer.tobytes())
        text = f"⚠️ Alerta: {len(detections)} persona(s) detectada(s)!"
        try:
            resp = requests.post(
                self.api_url_photo,
                data={"chat_id": self.chat_id, "caption": text},
                files={"photo": photo_bytes},
                timeout=5
            )
            if resp.status_code != 200:
                print(f"[Telegram] Error al enviar alerta: {resp.status_code}")
                print(resp.text)
                success = False
        except Exception as e:
            print(f"[Telegram] Exception al enviar alerta: {e}")
            success = False

        # Si hay pose_frame, enviar también overlay
        if pose_frame is not None:
            _, buffer_pose = cv2.imencode(".png", pose_frame)
            pose_bytes = io.BytesIO(buffer_pose.tobytes())
            try:
                resp = requests.post(
                    self.api_url_photo,
                    data={"chat_id": self.chat_id, "caption": "Imagen con keypoints detectados"},
                    files={"photo": pose_bytes},
                    timeout=5
                )
                if resp.status_code != 200:
                    print(f"[Telegram] Error al enviar keypoints: {resp.status_code}")
                    print(resp.text)
                    success = False
            except Exception as e:
                print(f"[Telegram] Exception al enviar keypoints: {e}")
                success = False

        if success:
            print("[Telegram] Alertas enviadas correctamente")
        return success

        
