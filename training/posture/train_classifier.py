import argparse
import os

import joblib
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC

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
    parser = argparse.ArgumentParser(description="Entrenar clasificador de posturas.")
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT,
        help="CSV con keypoints y etiquetas.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_MODEL,
        help="Ruta de salida del modelo entrenado.",
    )
    args = parser.parse_args()

    labels, X = _load_csv(args.input)
    unique_labels = sorted(set(labels))
    label_to_id = {label: idx for idx, label in enumerate(unique_labels)}
    y = np.array([label_to_id[l] for l in labels], dtype=np.int32)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = LinearSVC()
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print("\n=== RESULTADOS ===")
    print("Precisión (accuracy):", acc)
    print("\nMatriz de confusión:\n", confusion_matrix(y_test, y_pred))
    print("\nReporte:\n", classification_report(y_test, y_pred, digits=4))

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    joblib.dump({"model": clf, "labels": unique_labels}, args.output)
    print(f"\n[OK] Modelo guardado en {args.output}")


if __name__ == "__main__":
    main()
