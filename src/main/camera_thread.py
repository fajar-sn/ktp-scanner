import cv2
from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QImage
import numpy

class CameraThread(QThread):
    change_pixmap = pyqtSignal(QImage, numpy.ndarray)
    current_webcam_index = 0
    is_running = True

    def run(self):
        print("\nrunning")
        cap = cv2.VideoCapture(self.current_webcam_index)

        while self.is_running:
            ret, frame = cap.read()

            if not ret:
                print("Failed to grab frame")
                break

            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = convert_to_qt_format.scaled(640, 480, Qt.KeepAspectRatio)
            self.change_pixmap.emit(p, rgb_image)
