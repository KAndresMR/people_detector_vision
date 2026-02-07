"""
Backend API - People Detector
Endpoint: POST /api/v1/detect
"""

import base64
import cv2
import numpy as np
import os

from backend.services.telegram_service import TelegramService
from backend.services.pose_service import process_image_with_pose
from flask import Flask, request, jsonify
from datetime import datetime

# Inicializamos el servicios
telegram = TelegramService()

app = Flask(__name__)

# ========== CONFIGURACIÓN ==========
UPLOAD_FOLDER = "backend/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ========== DETECTOR HOG (SIMULADO POR AHORA) ==========
def detect_people(image):
    """
    Detecta personas en la imagen usando HOG+SVM de OpenCV
    Por ahora es simulado, luego integras el detector real
    """
    # Inicializar HOG Descriptor
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    
    # Redimensionar para mejor rendimiento
    scale = 0.5
    small = cv2.resize(image, None, fx=scale, fy=scale)
    
    # Detectar personas
    boxes, weights = hog.detectMultiScale(
        small,
        0,              # hitThreshold
        (8, 8),         # winStride
        (32, 32),       # padding
        1.05,           # scale
        2.0             # finalThreshold (ahora posicional, no keyword)
    )
    
    # Escalar boxes de vuelta al tamaño original
    detections = []
    for i, (x, y, w, h) in enumerate(boxes):
        detection = {
            "person_detected": True,
            "confidence": float(weights[i]) if len(weights) > i else 0.9,
            "bbox": [
                int(x / scale),
                int(y / scale),
                int(w / scale),
                int(h / scale)
            ]
        }
        detections.append(detection)     
    return detections

# ========== ENDPOINT PRINCIPAL ==========
@app.route('/api/v1/detect', methods=['POST'])
def detect():
    """
    POST /api/v1/detect
    
    Request JSON:
    {
        "source": "desktop_app",
        "image": {
            "encoded": true,
            "format": "jpg",
            "data": "<base64_string>"
        }
    }
    
    Response JSON:
    {
        "backend_status": "ONLINE",
        "alert_sent": false,
        "detections": [
            {
                "person_detected": true,
                "confidence": 0.95,
                "bbox": [x, y, w, h]
            }
        ]
    }
    """
    try:
        # Validar request
        if not request.json:
            return jsonify({
                "error": "No JSON data received",
                "backend_status": "ERROR"
            }), 400
        
        data = request.json
        
        # Validar campos requeridos
        if "image" not in data or "data" not in data["image"]:
            return jsonify({
                "error": "Missing image data",
                "backend_status": "ERROR"
            }), 400
        
        # Decodificar imagen base64
        try:
            image_data = data["image"]["data"]
            image_bytes = base64.b64decode(image_data)
            
            # Convertir a numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            
            # Decodificar imagen
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("No se pudo decodificar la imagen")
            
        except Exception as e:
            return jsonify({
                "error": f"Error decoding image: {str(e)}",
                "backend_status": "ERROR"
            }), 400
        
        print(f"[BACKEND] Imagen recibida: {image.shape}")
        
        # ========== DETECTAR PERSONAS ==========
        detections = detect_people(image)
        
        print(f"[BACKEND] Detecciones: {len(detections)}")
        
        # ========== GUARDAR IMAGEN SI HAY DETECCIONES ==========
        alert_sent = False
        if len(detections) > 0:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"detection_{timestamp}.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Dibujar boxes
            image_with_boxes = image.copy()
            for det in detections:
                x, y, w, h = det["bbox"]
                cv2.rectangle(image_with_boxes, (x, y), (x+w, y+h), (0, 255, 0), 2)
                conf_text = f"{det['confidence']:.2f}"
                cv2.putText(image_with_boxes, conf_text, (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Guardar evidencia
            cv2.imwrite(filepath, image_with_boxes)
            print(f"[BACKEND] Imagen guardada: {filepath}")
            
            
            # === NUEVO ===
            # Aplicar MediaPipe para keypoints (opcional)
            pose_image = process_image_with_pose(image_with_boxes)
            
            # Enviar alerta a Telegram
            alert_sent = telegram.send_alert(image_with_boxes, detections, pose_frame=pose_image)
            if not alert_sent:
                print("[BACKEND] La alerta no se pudo enviar al bot")

            
        # ========== RESPUESTA ==========
        response = {
            "backend_status": "ONLINE",
            "alert_sent": alert_sent,
            "detections": detections,
            "timestamp": datetime.now().isoformat(),
            "source": data.get("source", "unknown")
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"[BACKEND] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "error": str(e),
            "backend_status": "ERROR",
            "detections": []
        }), 500

# ========== ENDPOINT DE HEALTH CHECK ==========
@app.route('/api/v1/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ONLINE",
        "service": "People Detector Backend",
        "version": "1.0.0"
    }), 200

# ========== ENDPOINT RAÍZ ==========
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "service": "People Detector Backend",
        "endpoints": {
            "detect": "POST /api/v1/detect",
            "health": "GET /api/v1/health"
        }
    }), 200

# ========== MANEJO DE ERRORES ==========
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "backend_status": "ERROR"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "backend_status": "ERROR"
    }), 500

# ========== MAIN ==========
if __name__ == "__main__":
    print("="*50)
    print("  People Detector Backend API")
    print("="*50)
    print("  Endpoints:")
    print("    POST http://127.0.0.1:5001/api/v1/detect")
    print("    GET  http://127.0.0.1:5001/api/v1/health")
    print("="*50)
    print()
    
    app.run(host="0.0.0.0", port=5001, debug=True)
