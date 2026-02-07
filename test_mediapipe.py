import cv2
import mediapipe as mp

# Inicializar Mediapipe pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Usar cámara
cap = cv2.VideoCapture(0)  # 0 = cámara principal

with mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    enable_segmentation=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as pose:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("No se pudo capturar frame")
            break

        # Convertir BGR a RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        # Dibujar landmarks si se detecta
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=3),
                mp_drawing.DrawingSpec(color=(0,0,255), thickness=2)
            )

        # Mostrar
        cv2.imshow("Mediapipe Pose", frame)

        # Salir con ESC
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
