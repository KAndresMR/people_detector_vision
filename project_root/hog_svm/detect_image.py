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
# HOG + SVM
# -------------------------------
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# -------------------------------
# IMAGEN
# -------------------------------
img = cv2.imread("imagen.jpg")
if img is None:
    raise FileNotFoundError("No se pudo cargar la imagen")

img = cv2.resize(img, (1200, 800))

# -------------------------------
# DETECCIÓN
# -------------------------------
rects, weights = hog.detectMultiScale(
    img,
    winStride=WIN_STRIDE,
    padding=PADDING,
    scale=SCALE
)

# -------------------------------
# FILTRADO
# -------------------------------
filtered_rects = []
filtered_weights = []

for (x, y, w, h), weight in zip(rects, weights):
    if weight >= SCORE_THRESHOLD:
        filtered_rects.append((x, y, w, h))
        filtered_weights.append(weight)

# -------------------------------
# DIBUJAR
# -------------------------------
for (x, y, w, h), weight in zip(filtered_rects, filtered_weights):
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(
        img,
        f"{weight:.2f}",
        (x, y - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        1
    )

# -------------------------------
# RESULTADO
# -------------------------------
cv2.imshow("HOG + SVM - Deteccion de Personas", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
