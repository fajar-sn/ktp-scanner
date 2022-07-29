import sqlite3

from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex


class CustomTableModel(QAbstractTableModel):
    def __init__(self):
        super(CustomTableModel, self).__init__()
        self.extracted_data = []

    def rowCount(self, index):
        return len(self.extracted_data)

    def columnCount(self, parent=QModelIndex()):
        return 19

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ("ID", "Provinsi", "Kabupaten/Kota", "NIK", "Nama", "Tempat Lahir", "Tanggal Lahir", "Jenis Kelamin", "Golongan Darah", "Alamat", "RT/RW", "Kelurahan/Desa", "Kecamatan", "Agama", "Status Perkawinan", "Pekerjaan", "Kewarganegaraan", "Berlaku Hingga", "Aksi")[section]
        else:
            return f"{section}"

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self.extracted_data[index.row()][index.column()] = value
            connection = sqlite3.connect('ktp-scanner.db')
            cursor = connection.cursor()

            if index.column() == 1:
                cursor.execute("UPDATE ktp_information SET province = :value WHERE id = :id", {
                               'value': value, 'id': index.row() + 1})
            elif index.column() == 2:
                cursor.execute("UPDATE ktp_information SET regency = :value WHERE id = :id", {
                               'value': value, 'id': index.row() + 1})
            elif index.column() == 3:
                cursor.execute("UPDATE ktp_information SET ktp_id = :value WHERE id = :id", {
                               'value': value, 'id': index.row() + 1})
            elif index.column() == 4:
                cursor.execute("UPDATE ktp_information SET name = :value WHERE id = :id", {
                               'value': value, 'id': index.row() + 1})
            elif index.column() == 5:
                cursor.execute("UPDATE ktp_information SET birth_place = :value WHERE id = :id", {
                               'value': value, 'id': index.row() + 1})
            elif index.column() == 6:
                cursor.execute("UPDATE ktp_information SET birth_date = :value WHERE id = :id", {
                               'value': value, 'id': index.row() + 1})
            elif index.column() == 7:
                cursor.execute("UPDATE ktp_information SET blood_group = :value WHERE id = :id", {
                               'value': value, 'id': index.row() + 1})
            elif index.column() == 8:
                cursor.execute("UPDATE ktp_information SET gender = :value WHERE id = :id", {
                               'value': value, 'id': index.row() + 1})
            elif index.column() == 9:
                cursor.execute("UPDATE ktp_information SET address = :value WHERE id = :id", {
                               'value': value, 'id': index.row() + 1})
            elif index.column() == 10:
                cursor.execute("UPDATE ktp_information SET rtrw = :value WHERE id = :id", {
                               'value': value, 'id': index.row() + 1})
            elif index.column() == 11:
                cursor.execute("UPDATE ktp_information SET village = :value WHERE id = :id", {
                               'value': value, 'id': index.row() + 1})
            elif index.column() == 12:
                cursor.execute("UPDATE ktp_information SET district = :value WHERE id = :id", {
                               'value': value, 'id': index.row() + 1})
            elif index.column() == 13:
                cursor.execute("UPDATE ktp_information SET relligion = :value WHERE id = :id", {
                               'value': value, 'id': index.row() + 1})
            elif index.column() == 14:
                cursor.execute("UPDATE ktp_information SET marriage_status = :value WHERE id = :id", {
                               'value': value, 'id': index.row() + 1})
            elif index.column() == 15:
                cursor.execute("UPDATE ktp_information SET job = :value WHERE id = :id", {
                               'value': value, 'id': index.row() + 1})
            elif index.column() == 16:
                cursor.execute("UPDATE ktp_information SET citizenship = :value WHERE id = :id", {
                               'value': value, 'id': index.row() + 1})
            elif index.column() == 17:
                cursor.execute("UPDATE ktp_information SET valid_until = :value WHERE id = :id", {
                               'value': value, 'id': index.row() + 1})

            connection.commit()
            connection.close()
            return True

        return False

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return

        value = self.extracted_data[index.row()][index.column()]

        if not type(value) is str:
            return value

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return str(value)
