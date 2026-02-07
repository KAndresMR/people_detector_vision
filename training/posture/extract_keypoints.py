import argparse
import csv
import os

import cv2
import mediapipe as mp

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_INPUT_DIR = os.path.join(BASE_DIR, "datasets", "posture_classification")
DEFAULT_OUTPUT = os.path.join(BASE_DIR, "training", "posture", "keypoints.csv")

mp_pose = mp.solutions.pose


def _iter_images(root_dir: str):
    valid_ext = (".jpg", ".jpeg", ".png")
    for label_name in sorted(os.listdir(root_dir)):
        class_dir = os.path.join(root_dir, label_name)
        if not os.path.isdir(class_dir):
            continue
        for fname in sorted(os.listdir(class_dir)):
            if fname.lower().endswith(valid_ext):
                yield label_name, os.path.join(class_dir, fname)


def extract_keypoints(input_dir: str, output_csv: str, max_per_class: int | None) -> None:
    if not os.path.isdir(input_dir):
        raise FileNotFoundError(f"No existe el directorio: {input_dir}")

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    header = ["label"]
    for i in range(33):
        header.extend([f"x{i}", f"y{i}", f"z{i}", f"v{i}"])

    counts = {}
    with mp_pose.Pose(static_image_mode=True) as pose, open(
        output_csv, "w", newline=""
    ) as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for label_name, image_path in _iter_images(input_dir):
            counts.setdefault(label_name, 0)
            if max_per_class is not None and counts[label_name] >= max_per_class:
                continue

            image = cv2.imread(image_path)
            if image is None:
                continue

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
            if not results.pose_landmarks:
                continue

            row = [label_name]
            for lm in results.pose_landmarks.landmark:
                row.extend([lm.x, lm.y, lm.z, lm.visibility])

            writer.writerow(row)
            counts[label_name] += 1

    print(f"[OK] CSV generado en {output_csv}")
    for label, count in sorted(counts.items()):
        print(f" - {label}: {count}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extraer keypoints con MediaPipe.")
    parser.add_argument(
        "--input-dir",
        default=DEFAULT_INPUT_DIR,
        help="Directorio con carpetas de clases.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="Ruta del CSV de salida.",
    )
    parser.add_argument(
        "--max-per-class",
        type=int,
        default=None,
        help="Máximo de imágenes por clase (opcional).",
    )
    args = parser.parse_args()

    extract_keypoints(args.input_dir, args.output, args.max_per_class)


if __name__ == "__main__":
    main()
