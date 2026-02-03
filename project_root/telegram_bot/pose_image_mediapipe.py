import cv2
import mediapipe as mp
import time
import os
import psutil

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def run_pose_image(input_img, output_img):
    image = cv2.imread(input_img)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    process = psutil.Process(os.getpid())
    start_time = time.time()

    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

    elapsed = time.time() - start_time
    ram_mb = process.memory_info().rss / (1024 * 1024)

    cv2.imwrite(output_img, image)

    return {
        "time_sec": round(elapsed, 2),
        "ram_mb": round(ram_mb, 2)
    }
