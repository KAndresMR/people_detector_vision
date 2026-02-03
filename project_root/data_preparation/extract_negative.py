import cv2
import os
import glob

VIDEO_DIR = "dataset/raw/videos"
OUTPUT_DIR = "dataset/negatives"

os.makedirs(OUTPUT_DIR, exist_ok=True)

videos = glob.glob(os.path.join(VIDEO_DIR, "no_people_video_*.mp4"))

frame_id = 0
saved = 0

for video_path in videos:
    print(f"[INFO] Procesando {video_path}")
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % 1 == 0:
            filename = f"neg_{saved:05d}.jpg"
            cv2.imwrite(os.path.join(OUTPUT_DIR, filename), frame)
            saved += 1

        frame_id += 1

    cap.release()

print(f"[OK] Total imágenes negativas guardadas: {saved}")