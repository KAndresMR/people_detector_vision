import cv2
import mediapipe as mp
import time
import os

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

def run_pose_video(input_path: str, output_path: str):

    cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        print(" Error: no se pudo abrir el video")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(" run_pose_video: Iniciando")
    print(" FPS:", fps, "W:", w, "H:", h)

    # Asegurar carpeta de salida
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    #  Codec compatible en Linux/Mac/Windows
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    frame_count = 0
    detected_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = pose.process(img_rgb)

        if results.pose_landmarks:
            detected_count += 1
            mp_draw.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

        out.write(frame)

    cap.release()
    out.release()
    pose.close()

    print(" Frames totales:", frame_count)
    print(" Frames detectados:", detected_count)
    print(" Video finalizado. Output:", output_path)

    return output_path
