import argparse
import os

import cv2

# -------------------------------
# CONFIGURACIÓN AJUSTADA
# -------------------------------
WIN_STRIDE = (4, 4)
PADDING = (8, 8)
SCALE = 1.03
SCORE_THRESHOLD = 0.3

def _build_hog():
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    return hog


def _ensure_output_dir(path: str) -> None:
    output_dir = os.path.dirname(path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)


def detect_image(image_path: str, output_path: str | None, show: bool) -> None:
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar la imagen: {image_path}")

    img = cv2.resize(img, (1200, 800))

    hog = _build_hog()
    rects, weights = hog.detectMultiScale(
        img,
        winStride=WIN_STRIDE,
        padding=PADDING,
        scale=SCALE,
    )

    for (x, y, w, h), weight in zip(rects, weights):
        if weight >= SCORE_THRESHOLD:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                img,
                f"{weight:.2f}",
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )

    if output_path:
        _ensure_output_dir(output_path)
        cv2.imwrite(output_path, img)

    if show:
        cv2.imshow("HOG + SVM - Deteccion de Personas", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main() -> None:
    parser = argparse.ArgumentParser(description="Detectar personas en una imagen.")
    parser.add_argument("--image", required=True, help="Ruta de la imagen de entrada.")
    parser.add_argument(
        "--output",
        default=None,
        help="Ruta de salida de la imagen anotada (opcional).",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="No mostrar ventana de resultados.",
    )
    args = parser.parse_args()

    detect_image(args.image, args.output, show=not args.no_show)


if __name__ == "__main__":
    main()
