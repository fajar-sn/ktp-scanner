from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex

class CustomTableModel(QAbstractTableModel):
    def __init__(self):
        super(CustomTableModel, self).__init__()
        self.extracted_data = []
        print(f'data {self.extracted_data}')

    def rowCount(self, index):
        return len(self.extracted_data)

    def columnCount(self, parent=QModelIndex()):
        return 15

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ("NIK", "Nama", "Tempat Lahir", "Tanggal Lahir", "Jenis Kelamin", "Golongan Darah", "Alamat", "RT/RW", "Kelurahan/Desa", "Kecamatan", "Agama", "Status Perkawinan", "Pekerjaan", "Kewarganegaraan", "Berlaku Hingga")[section]
            # return ("NIK", "Nama", "Aksi")[section]
        else:
            return f"{section}"


    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self.extracted_data[index.row()][index.column()])

        return None

    # def flags(self, index):
    #     return Qt.ItemIsSelectable|Qt.ItemIsEnabled|Qt.ItemIsEditable

    # def setData(self, index, value, role):
    #     if role == Qt.EditRole:
    #         self._data[index.row()][index.column()] = value
    #         return True
        
    #     return False
    # def insert_rows(self, position, rows, ):
        
