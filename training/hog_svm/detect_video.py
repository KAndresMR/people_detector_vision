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

DEFAULT_FPS = 30.0


def _ensure_output_dir(path: str) -> None:
    output_dir = os.path.dirname(path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)


def _build_hog():
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    return hog


def detect_video(input_path: str, output_path: str, show: bool) -> None:
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"No se pudo abrir el video: {input_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = DEFAULT_FPS

    _ensure_output_dir(output_path)
    out = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    hog = _build_hog()

    print(" Procesando video...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (width, height))

        rects, weights = hog.detectMultiScale(
            frame,
            winStride=WIN_STRIDE,
            padding=PADDING,
            scale=SCALE,
        )

        for (x, y, w, h), weight in zip(rects, weights):
            if weight >= SCORE_THRESHOLD:
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2,
                )
                cv2.putText(
                    frame,
                    f"{weight:.2f}",
                    (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )

        out.write(frame)
        if show:
            cv2.imshow("HOG + SVM - Deteccion de Personas (Video)", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    cap.release()
    out.release()
    if show:
        cv2.destroyAllWindows()

    print(f" Video guardado como {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Detectar personas en un video.")
    parser.add_argument("--video", required=True, help="Ruta del video de entrada.")
    parser.add_argument(
        "--output",
        default="resultado_video.mp4",
        help="Ruta de salida del video anotado.",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="No mostrar ventana de resultados.",
    )
    args = parser.parse_args()

    detect_video(args.video, args.output, show=not args.no_show)


if __name__ == "__main__":
    main()
