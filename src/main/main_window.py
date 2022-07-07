import os
import numpy
import csv
import win32com.client

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

from src.ocr_process.custom_table_model import CustomTableModel
from src.ocr_process.ocr_process import OcrProcess
from src.main.camera_thread import CameraThread


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.available_cameras = None
        self.capture = None
        self.viewfinder_label: QLabel = None
        self.custom_thread: CameraThread = CameraThread(self)
        self.viewfinder_image: numpy.ndarray = None
        self.selected_image: numpy.ndarray = None
        self.setup_view()
        self.setup_action()

    def setup_view(self) -> None:
        self.user_interface = uic.loadUi("./src/main/main_window.ui", self)
        self.take_picture_button: QPushButton = self.user_interface.take_picture_button
        self.extract_image_button: QPushButton = self.user_interface.extract_image_button
        self.save_table_button: QPushButton = self.user_interface.save_table_button
        self.camera_status_label: QLabel = self.user_interface.camera_status_label
        self.stacked_widget: QStackedWidget = self.user_interface.stacked_widget
        self.cameras_combo_box: QComboBox = self.user_interface.cameras_combo_box
        self.image_label: QLabel = self.user_interface.image_label
        self.table_view: QTableView = self.user_interface.table_view
        self.init_camera()
        self.table_model = CustomTableModel()
        self.table_view.setModel(self.table_model)

    def setup_action(self) -> None:
        self.cameras_combo_box.currentIndexChanged.connect(self.select_camera)
        self.take_picture_button.clicked.connect(self.take_picture)
        self.extract_image_button.clicked.connect(self.extract_image)
        self.save_table_button.clicked.connect(self.save_table)

    def init_camera(self) -> None:
        self.available_cameras = QCameraInfo.availableCameras()

        if not self.available_cameras:
            message = "Kamera tidak tersedia. Silahkan restart aplikasi."
            self.camera_status_label.setText(message)
            self.alert(message)

        self.cameras_combo_box.addItems(
            [camera.description() for camera in self.available_cameras])
        self.select_camera(0)

    def select_camera(self, i: int) -> None:
        self.viewfinder_label = QLabel(self)

        if self.custom_thread.isRunning():
            self.custom_thread.is_running = False
            self.custom_thread.quit()
            self.custom_thread = CameraThread(self)

        self.custom_thread.current_webcam_index = i
        self.custom_thread.change_pixmap.connect(self.set_image)
        self.custom_thread.start()

        if self.stacked_widget.count() != 0:
            current_widget = self.stacked_widget.currentWidget()
            self.stacked_widget.removeWidget(current_widget)

        self.stacked_widget.addWidget(self.viewfinder_label)

    @pyqtSlot(QImage, numpy.ndarray)
    def set_image(self, image: QImage, raw_image: numpy.ndarray):
        self.viewfinder_label.setPixmap(QPixmap.fromImage(image))
        self.viewfinder_image = raw_image

    def alert(self, message: str):
        error = QErrorMessage(self)
        error.showMessage(message)

    def take_picture(self):
        # For saving image purpose

        # timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")
        # file_name = f"./{timestamp}.jpg"
        # saved_image = cv2.cvtColor(self.viewfinder_image, cv2.COLOR_BGR2RGB)
        # cv2.imwrite(file_name, saved_image)

        self.selected_image = self.viewfinder_image

        h, w, ch = self.selected_image.shape
        bytes_per_line = ch * w
        q_image = QImage(self.selected_image.data, w, h,
                         bytes_per_line, QImage.Format_RGB888)
        q_image = q_image.scaled(800, 600, Qt.KeepAspectRatio)
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)

    def next_image_file_name(self) -> str:
        pictures_location = QStandardPaths.writableLocation(
            QStandardPaths.TempLocation)
        date_string = QDate.currentDate().toString("yyyyMMdd")
        pattern = f"{pictures_location}/pyqt5_camera_{date_string}_{{:03d}}.jpg"
        n = 1

        while True:
            result = pattern.format(n)

            if not os.path.exists(result):
                return result

            n = n + 1

    @pyqtSlot()
    def extract_image(self):
        try:
            ocr_process = OcrProcess(self.selected_image)
            ocr_result = ocr_process.result
            print(ocr_result.to_string())

            self.table_model.extracted_data.append([
                ocr_result.province,
                ocr_result.regency,
                ocr_result.id,
                ocr_result.name,
                ocr_result.birth_place,
                ocr_result.birth_date,
                ocr_result.gender,
                ocr_result.blood_group,
                ocr_result.address,
                ocr_result.rtrw,
                ocr_result.village,
                ocr_result.district,
                ocr_result.relligion,
                ocr_result.marriage_status,
                ocr_result.job,
                ocr_result.citizenship,
                ocr_result.valid_until,
                ''
            ])

            delete_button = QPushButton('Hapus')
            delete_button.clicked.connect(self.delete_button_on_click)
            row = len(self.table_model.extracted_data) - 1
            self.table_view.setIndexWidget(
                self.table_model.index(row, 17), delete_button)
            self.table_model.layoutChanged.emit()
        except Exception as exception:
            QMessageBox.critical(
                self,
                "Error",
                f"Error telah terjadi. Dapat terjadi karena kondisi dokumen yang tidak bisa terbaca oleh sistem.\nPenyebab: {exception}",
                buttons=QMessageBox.Ok
            )

    def closeEvent(self, event):
        # self.custom_thread.is_running = False
        # self.custom_thread.quit()
        # self.custom_thread.wait()

        reply = QMessageBox.question(
            self, "Keluar",
            "Apakah Anda yakin untuk keluar?",
            QMessageBox.Close | QMessageBox.Cancel,
            QMessageBox.Cancel)

        if reply == QMessageBox.Close:
            self.custom_thread.is_running = False
            self.custom_thread.quit()
            self.custom_thread.wait()
        else:
            pass

    @pyqtSlot()
    def delete_button_on_click(self):
        button = qApp.focusWidget()
        index = self.table_view.indexAt(button.pos())

        if not index.isValid():
            return

        reply = QMessageBox.question(
            self, "Hapus Data",
            f"Apakah Anda yakin untuk menghapus baris ke-{index.row()}")

        if reply == QMessageBox.Yes:
            self.table_model.extracted_data.remove(
                self.table_model.extracted_data[index.row()])
            self.table_model.layoutChanged.emit()

    @pyqtSlot()
    def save_table(self):
        oShell = win32com.client.Dispatch("Wscript.Shell")
        folder = oShell.SpecialFolders("Desktop")

        fileName, _ = QFileDialog.getSaveFileName(
            self, "Expor Tabel ke File Format CSV", folder, "CSV Files (*.csv);;All Files (*)")

        if not fileName:
            return

        print(fileName)
        outfile = open(fileName, 'w', newline='')
        writer = csv.writer(outfile)

        writer.writerow(["Provinsi", "Kabupaten/Kota", "NIK", "Nama", "Tempat Lahir", "Tanggal Lahir", "Jenis Kelamin", "Golongan Darah",
                        "Alamat", "RT/RW", "Kelurahan/Desa", "Kecamatan", "Agama", "Status Perkawinan", "Pekerjaan", "Kewarganegaraan", "Berlaku Hingga"])
        
        writer.writerows(self.table_model.extracted_data)
        
        QMessageBox.information(
            self, "Ekspor ke File Format CSV Berhasil", f"File berhasil diekspor ke {fileName}")
