import albumentations as A
import cv2
import os

augmenter = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.Rotate(limit=15, p=0.3),
    A.RandomBrightnessContrast(p=0.4),
    A.GaussNoise(p=0.2),
])

def clear_folder(folder):
    os.makedirs(folder, exist_ok=True)
    for f in os.listdir(folder):
        path = os.path.join(folder, f)
        if os.path.isfile(path):
            os.remove(path)

def augment_folder(input_dir, output_dir, times=10, out_size=(128, 256), jpg_quality=80):
    os.makedirs(output_dir, exist_ok=True)
    count = 0

    # solo imágenes válidas
    valid_ext = (".jpg", ".jpeg", ".png")

    img_list = [f for f in os.listdir(input_dir) if f.lower().endswith(valid_ext)]
    img_list.sort()

    for img_name in img_list:
        img_path = os.path.join(input_dir, img_name)
        image = cv2.imread(img_path)
        if image is None:
            continue

        # reducir tamaño base para acelerar
        image = cv2.resize(image, out_size)

        base_name, _ = os.path.splitext(img_name)

        for i in range(times):
            aug_img = augmenter(image=image)["image"]
            # asegurar tamaño final
            aug_img = cv2.resize(aug_img, out_size)

            out_name = f"{base_name}_aug_{i:02d}.jpg"
            cv2.imwrite(
                os.path.join(output_dir, out_name),
                aug_img,
                [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality]
            )
            count += 1

    print(f"[OK] {count} imágenes generadas en {output_dir}")

if __name__ == "__main__":
    # (recomendado) limpiar para no duplicar
    clear_folder("dataset/positives_aug")
    clear_folder("dataset/negatives_aug")

    # Ajusta times según tus cantidades reales
    augment_folder("dataset/positives", "dataset/positives_aug", times=10)
    augment_folder("dataset/negatives", "dataset/negatives_aug", times=10)