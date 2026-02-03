import cv2
import numpy as np

# -------------------------------
# CONFIGURACIÓN AJUSTADA
# -------------------------------
WIN_STRIDE = (4, 4)
PADDING = (8, 8)
SCALE = 1.03
SCORE_THRESHOLD = 0.3

# -------------------------------
# HOG + SVM (OpenCV preentrenado)
# -------------------------------
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# -------------------------------
# VIDEO ENTRADA
# -------------------------------
cap = cv2.VideoCapture("video.mp4")
if not cap.isOpened():
    raise RuntimeError("No se pudo abrir el video")

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# -------------------------------
# VIDEO SALIDA
# -------------------------------
out = cv2.VideoWriter(
    "resultado_video.mp4",
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (width, height)
)

print("🎥 Procesando video...")

# -------------------------------
# PROCESAR FRAMES
# -------------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (width, height))

    rects, weights = hog.detectMultiScale(
        frame,
        winStride=WIN_STRIDE,
        padding=PADDING,
        scale=SCALE
    )

    # -------------------------------
    # FILTRADO
    # -------------------------------
    for (x, y, w, h), weight in zip(rects, weights):
        if weight >= SCORE_THRESHOLD:
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )
            cv2.putText(
                frame,
                f"{weight:.2f}",
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1
            )

    out.write(frame)
    cv2.imshow("HOG + SVM - Deteccion de Personas (Video)", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

# -------------------------------
# CERRAR
# -------------------------------
cap.release()
out.release()
cv2.destroyAllWindows()

print(" Video guardado como resultado_video.mp4")
