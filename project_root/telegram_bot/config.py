BOT_TOKEN = "8303583213:AAFXQ_AefKqHb772DidJgJsSPdInXGVL3Tc"

import os
import cv2
import mediapipe as mp
import time
import psutil

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils
