import os
import cv2
import numpy as np
from skimage.feature import hog
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib

POS_DIRS = ["dataset/positives", "dataset/positives_aug"]
NEG_DIRS = ["dataset/negatives", "dataset/negatives_aug"]

IMG_SIZE = (128, 256)  # (w, h) típico para peatones
MAX_PER_CLASS = 4500   # para balancear (no uses 8000 vs 4000)

def load_images(dirs, label, max_count):
    X, y = [], []
    count = 0
    valid_ext = (".jpg", ".jpeg", ".png")

    for d in dirs:
        if not os.path.isdir(d):
            continue
        files = [f for f in os.listdir(d) if f.lower().endswith(valid_ext)]
        files.sort()

        for fname in files:
            if count >= max_count:
                break
            path = os.path.join(d, fname)
            img = cv2.imread(path)
            if img is None:
                continue

            img = cv2.resize(img, IMG_SIZE)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            feat = hog(
                gray,
                orientations=9,
                pixels_per_cell=(8, 8),
                cells_per_block=(2, 2),
                block_norm="L2-Hys"
            )
            X.append(feat)
            y.append(label)
            count += 1

        if count >= max_count:
            break

    print(f"[INFO] Cargadas {count} imágenes label={label}")
    return np.array(X), np.array(y)

def main():
    # Balancear clases: usamos el mínimo entre positivos/negativos disponibles
    X_pos, y_pos = load_images(POS_DIRS, 1, MAX_PER_CLASS)
    X_neg, y_neg = load_images(NEG_DIRS, 0, MAX_PER_CLASS)

    X = np.vstack([X_pos, X_neg])
    y = np.hstack([y_pos, y_neg])

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

    os.makedirs("hog_svm", exist_ok=True)
    joblib.dump(clf, "hog_svm/hog_svm_model.pkl")
    print("\n[OK] Modelo guardado en hog_svm/hog_svm_model.pkl")

if __name__ == "__main__":
    main()