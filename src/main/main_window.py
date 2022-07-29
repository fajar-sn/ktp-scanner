import os
import numpy
import csv
import win32com.client
import sqlite3
# import time
# import cv2

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
        self.setup_local_database()

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

    def setup_local_database(self):
        connection = sqlite3.connect('ktp-scanner.db')
        db_cursor = connection.cursor()

        db_cursor.execute("""CREATE TABLE IF NOT EXISTS ktp_information(
            id text,
            province text,
            regency text,
            ktp_id text,
            name text,
            birth_place text,
            birth_date text,
            gender text,
            blood_group text,
            address text,
            rtrw text,
            village text,
            district text,
            relligion text,
            marriage_status text,
            job text,
            citizenship text,
            valid_until text
        )""")

        db_cursor.execute("SELECT * FROM ktp_information")
        records = db_cursor.fetchall()

        for record in records:
            edited_record = list(record)
            print(edited_record)
            edited_record.append('')
            self.table_model.extracted_data.append(edited_record)

            delete_button = QPushButton('Hapus')
            delete_button.clicked.connect(self.delete_button_on_click)
            row = len(self.table_model.extracted_data) - 1
            self.table_view.setIndexWidget(
                self.table_model.index(row, 18), delete_button)
            self.table_model.layoutChanged.emit()

        connection.commit()
        connection.close()

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
        # file_name = f"./{timestamp} -1.jpg"
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
                f'{len(self.table_model.extracted_data) + 1}',
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
                self.table_model.index(row, 18), delete_button)
            self.table_model.layoutChanged.emit()

            connection = sqlite3.connect('ktp-scanner.db')
            cursor = connection.cursor()
            # cursor.execute("DELETE FROM ktp_information;",)

            cursor.execute("INSERT INTO ktp_information VALUES (:id, :province, :regency, :ktp_id, :name, :birth_place, :birth_date, :gender, :blood_group, :address, :rtrw, :village, :district, :relligion, :marriage_status, :job, :citizenship, :valid_until)", {
                'id': f'{len(self.table_model.extracted_data)}',
                'province': ocr_result.province,
                'regency': ocr_result.regency,
                'ktp_id': ocr_result.id,
                'name': ocr_result.name,
                'birth_place': ocr_result.birth_place,
                'birth_date': ocr_result.birth_date,
                'gender': ocr_result.gender,
                'blood_group': ocr_result.blood_group,
                'address': ocr_result.address,
                'rtrw': ocr_result.rtrw,
                'village': ocr_result.village,
                'district': ocr_result.district,
                'relligion': ocr_result.relligion,
                'marriage_status': ocr_result.marriage_status,
                'job': ocr_result.job,
                'citizenship': ocr_result.citizenship,
                'valid_until': ocr_result.valid_until,
            })

            connection.commit()
            connection.close()
        except Exception as exception:
            print(f"\n{exception}\n")
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
            connection = sqlite3.connect('ktp-scanner.db')
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM ktp_information WHERE id = {index.row() + 1}")
            connection.commit()
            connection.close()
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

        writer.writerow(["ID, Provinsi", "Kabupaten/Kota", "NIK", "Nama", "Tempat Lahir", "Tanggal Lahir", "Jenis Kelamin", "Golongan Darah",
                        "Alamat", "RT/RW", "Kelurahan/Desa", "Kecamatan", "Agama", "Status Perkawinan", "Pekerjaan", "Kewarganegaraan", "Berlaku Hingga"])

        writer.writerows(self.table_model.extracted_data)

        QMessageBox.information(
            self, "Ekspor ke File Format CSV Berhasil", f"File berhasil diekspor ke {fileName}")
