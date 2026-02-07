import argparse
import os

import joblib
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_INPUT = os.path.join(BASE_DIR, "training", "posture", "keypoints.csv")
DEFAULT_MODEL = os.path.join(BASE_DIR, "models", "posture_classifier.pkl")


def _load_csv(path: str):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No existe el CSV: {path}")

    data = np.loadtxt(path, delimiter=",", dtype=str)
    if data.ndim == 1:
        data = data.reshape(1, -1)
    if data.shape[0] <= 1:
        raise ValueError("El CSV no contiene datos (solo encabezado).")
    labels = data[1:, 0]
    features = data[1:, 1:].astype(np.float32)
    return labels, features


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluar clasificador de posturas.")
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT,
        help="CSV con keypoints y etiquetas.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Ruta del modelo entrenado.",
    )
    args = parser.parse_args()

    labels, X = _load_csv(args.input)
    payload = joblib.load(args.model)
    clf = payload["model"]
    label_list = payload["labels"]
    label_to_id = {label: idx for idx, label in enumerate(label_list)}
    y = np.array([label_to_id[l] for l in labels], dtype=np.int32)

    y_pred = clf.predict(X)
    acc = accuracy_score(y, y_pred)

    print("\n=== RESULTADOS ===")
    print("Precisión (accuracy):", acc)
    print("\nMatriz de confusión:\n", confusion_matrix(y, y_pred))
    print("\nReporte:\n", classification_report(y, y_pred, digits=4))


if __name__ == "__main__":
    main()
