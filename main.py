import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time

# Inisialisasi MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

screen_width, screen_height = pyautogui.size()

cap = cv2.VideoCapture(0)
cam_width, cam_height = 640, 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)

padding = 100
click_delay_left = 0.5
click_delay_right = 0.8
last_click_time_left = 0
last_click_time_right = 0
ema_x, ema_y = 0, 0
prev_ema_x, prev_ema_y = 0, 0
prev_time = time.time()
dragging = False
calibrate_active = False
recalibrate_offset_x = 0
recalibrate_offset_y = 0

scroll_velocity = 0
scroll_decay = 0.85
scrolling_active = False

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Ambil landmark penting
            index_tip = hand_landmarks.landmark[8]
            middle_tip = hand_landmarks.landmark[12]
            thumb_tip = hand_landmarks.landmark[4]
            ring_tip = hand_landmarks.landmark[16]
            pinky_tip = hand_landmarks.landmark[20]

            ix = int(index_tip.x * cam_width)
            iy = int(index_tip.y * cam_height)
            tx = int(thumb_tip.x * cam_width)
            ty = int(thumb_tip.y * cam_height)

            norm_x = index_tip.x
            norm_y = index_tip.y

            # Mapping ke layar
            screen_x = np.interp(norm_x, (padding / cam_width, 1 - padding / cam_width), (0, screen_width))
            screen_y = np.interp(norm_y, (padding / cam_height, 1 - padding / cam_height), (0, screen_height))

            if calibrate_active:
                recalibrate_offset_x = screen_x
                recalibrate_offset_y = screen_y
                calibrate_active = False

            screen_x -= recalibrate_offset_x
            screen_y -= recalibrate_offset_y

            # Smooth cursor
            dx = screen_x - prev_ema_x
            dy = screen_y - prev_ema_y
            speed = math.hypot(dx, dy)
            dynamic_alpha = min(max(0.05 + speed / 50, 0.1), 0.3)
            ema_x = prev_ema_x * (1 - dynamic_alpha) + screen_x * dynamic_alpha
            ema_y = prev_ema_y * (1 - dynamic_alpha) + screen_y * dynamic_alpha
            prev_ema_x, prev_ema_y = ema_x, ema_y

            pyautogui.moveTo(ema_x, ema_y)
            cv2.circle(img, (ix, iy), 10, (255, 0, 255), cv2.FILLED)

            # Deteksi klik
            dist_thumb_index = math.hypot(tx - ix, ty - iy)
            dist_index_middle = math.hypot(
                int(index_tip.x * cam_width) - int(middle_tip.x * cam_width),
                int(index_tip.y * cam_height) - int(middle_tip.y * cam_height)
            )
            current_time = time.time()

            # Klik kiri
            if dist_thumb_index < 30 and not dragging:
                if current_time - last_click_time_left > click_delay_left:
                    last_click_time_left = current_time
                    pyautogui.click()
                    cv2.circle(img, (ix, iy), 15, (0, 255, 0), cv2.FILLED)

            # Klik kanan
            if dist_index_middle < 20:
                if current_time - last_click_time_right > click_delay_right:
                    last_click_time_right = current_time
                    pyautogui.rightClick()
                    cv2.circle(img, (ix, iy), 15, (0, 255, 255), cv2.FILLED)

            # Drag
            if dist_thumb_index < 25:
                if not dragging:
                    pyautogui.mouseDown()
                    dragging = True
            else:
                if dragging:
                    pyautogui.mouseUp()
                    dragging = False

            # Scroll dengan kombinasi jari
            thumb_x, thumb_y = int(thumb_tip.x * cam_width), int(thumb_tip.y * cam_height)
            ring_x, ring_y = int(ring_tip.x * cam_width), int(ring_tip.y * cam_height)
            pinky_x, pinky_y = int(pinky_tip.x * cam_width), int(pinky_tip.y * cam_height)

            dist_thumb_ring = math.hypot(thumb_x - ring_x, thumb_y - ring_y)
            dist_thumb_pinky = math.hypot(thumb_x - pinky_x, thumb_y - pinky_y)

            scrolling_active = False
            if dist_thumb_ring < 40:  # jari manis + ibu jari
                scroll_velocity = max(scroll_velocity - 5, -20)  # scroll down
                scrolling_active = True
            elif dist_thumb_pinky < 40:  # kelingking + ibu jari
                scroll_velocity = min(scroll_velocity + 5, 20)  # scroll up
                scrolling_active = True

    # Scroll inertia
    if abs(scroll_velocity) > 1:
        pyautogui.scroll(int(scroll_velocity))
        scroll_velocity *= scroll_decay

    # FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time + 1e-6)
    prev_time = curr_time
    cv2.putText(img, f'FPS: {int(fps)}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 255, 50), 2)

    if scrolling_active:
        cv2.putText(img, 'SCROLLING', (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 255), 2)

    cv2.imshow("Virtual Mouse", img)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break
    elif key == 32:
        calibrate_active = True

    time.sleep(0.01)

cap.release()
cv2.destroyAllWindows()
