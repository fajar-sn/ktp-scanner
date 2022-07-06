import cv2
import numpy

from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QImage

class CameraThread(QThread):
    change_pixmap = pyqtSignal(QImage, numpy.ndarray)
    current_webcam_index = 0
    is_running = True

    def run(self):
        # cap: cv2.VideoCapture = cv2.VideoCapture(self.current_webcam_index, cv2.CAP_V4L)
        # cap = cv2.VideoCapture(self.current_webcam_index)
        cap = cv2.VideoCapture(self.current_webcam_index, cv2.CAP_DSHOW)

        while self.is_running:
            ret, frame = cap.read()

            if not ret:
                break

            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = convert_to_qt_format.scaled(640, 480, Qt.KeepAspectRatio)
            self.change_pixmap.emit(p, rgb_image)
