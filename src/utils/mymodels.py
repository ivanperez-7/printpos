from datetime import datetime

from PySide6.QtCore import Qt, QAbstractTableModel, QSortFilterProxyModel
from PySide6.QtGui import QColor, QFont

from utils.myutils import ColorsEnum, formatDate


class GenericModel(QAbstractTableModel):
    def __init__(self, data: list[tuple], headers: list[str]):
        super().__init__()
        self._data = data or [[''] * len(headers)]
        self._headers = headers
    
    def data(self, index, role):
        cell = self._data[index.row()][index.column()]
        header = self._headers[index.column()]
        
        if role == Qt.DisplayRole:    
            if isinstance(cell, datetime):
                return formatDate(cell)
            if isinstance(cell, float):
                if header == 'Descuento' and not cell:
                    return ''
                return f'{cell:,.2f}'
            
            return cell
        
        if role == Qt.FontRole:
            font = QFont('Segoe UI', 10)
            if header == 'Importe':
                font.setBold(True)
            return font
        
        if role == Qt.BackgroundRole:
            if header == 'Estado':
                if cell.startswith('Cancelada'):
                    return QColor(ColorsEnum.ROJO)
                if cell.startswith('Terminada'):
                    return QColor(ColorsEnum.VERDE)
                if cell.startswith('Recibido'):
                    return QColor(ColorsEnum.AMARILLO)
            
            if index.row()%2:
                return QColor("#F0F0F0")
            
            return QColor(Qt.white)

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])
    
    def headerData(self, section: int, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._headers[section]


class GenericFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, data: list[tuple], headers: list[str]):
        super().__init__()
        
        model = GenericModel(data, headers)
        
        self.setSourceModel(model)
        self.setFilterKeyColumn(1)
        self.setSourceModel(model)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
