# 🖱️ Virtual Mouse with Hand Gesture Control

This project turns your webcam into a **virtual mouse controller** using **hand gestures** powered by **MediaPipe**, **OpenCV**, and **PyAutoGUI**. You can move your cursor, click, drag, and scroll—all with your fingers!

## 🎯 Features

- 👆 Move the mouse using index finger tracking
- 👈 Left-click by pinching thumb and index finger
- 👉 Right-click by bringing index and middle fingers close
- ✊ Drag and drop using a strong thumb-index pinch
- 📜 Scroll up/down using thumb + pinky or thumb + ring finger gesture
- 📷 Real-time hand tracking using MediaPipe
- 🖥️ Smooth cursor movement with exponential moving average (EMA)
- ⚙️ Screen recalibration with spacebar (to fix misalignment)

## 🧠 Tech Stack

- [OpenCV](https://opencv.org/) - for webcam capture and image processing
- [MediaPipe](https://google.github.io/mediapipe/) - for hand tracking and landmark detection
- [PyAutoGUI](https://pyautogui.readthedocs.io/en/latest/) - for controlling the mouse
- [NumPy](https://numpy.org/) - for numeric operations
- [math](https://docs.python.org/3/library/math.html) & [time](https://docs.python.org/3/library/time.html) - standard Python libraries
