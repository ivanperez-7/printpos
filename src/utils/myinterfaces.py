""" Módulo para controladores de grupos de widgets y otras funciones. """
from PySide6.QtWidgets import *
from PySide6.QtCore import QDate, QObject, Signal


__all__ = ['InterfazPaginas', 'InterfazFechas', 'InterfazFiltro']


class InterfazPaginas(QObject):
    """ Interfaz para manejar paginados en tablas. 
        
        Lo único que hace esta interfaz es manejar la propiedad 
        `paginaActual` de la tabla asociada. """
    paginaCambiada = Signal()
    
    def __init__(self, btAdelante: QPushButton,
                 btUltimo: QPushButton,
                 btAtras: QPushButton,
                 btPrimero: QPushButton,
                 tabla_display: QTableWidget):
        super().__init__(tabla_display)
        
        self.tabla = tabla_display
        
        self.tabla.setProperty('paginaActual', 0)
        
        btAdelante.clicked.connect(self.ir_adelante)
        btUltimo.clicked.connect(self.ir_ultimo)
        btAtras.clicked.connect(self.ir_atras)
        btPrimero.clicked.connect(self.ir_primero)
    
    def ir_adelante(self):
        currentPage = self.tabla.property('paginaActual')
        self.tabla.setProperty('paginaActual', currentPage + 1)
        
        self.paginaCambiada.emit()
    
    def ir_ultimo(self):
        self.tabla.setProperty('paginaActual', 1e6)
        self.paginaCambiada.emit()
    
    def ir_atras(self):
        currentPage = self.tabla.property('paginaActual')
        self.tabla.setProperty('paginaActual', currentPage - 1)
        
        self.paginaCambiada.emit()
    
    def ir_primero(self):
        self.tabla.setProperty('paginaActual', 0)
        self.paginaCambiada.emit()


class InterfazFechas(QObject):
    """ Interfaz para manejar widgets de fechas desde y hasta,
        por medio de botones de 'Hoy', 'Esta semana' y 'Este mes'. """
    
    def __init__(self, btHoy: QPushButton,
                 btSemana: QPushButton,
                 btMes: QPushButton,
                 dateDesde: QDateEdit,
                 dateHasta: QDateEdit,
                 fechaMin: QDate = None):
        super().__init__(dateDesde)
        
        self.dateDesde = dateDesde
        self.dateHasta = dateHasta
        
        # configurar fechas permitidas
        hoy = QDate.currentDate()
        fechaMin = fechaMin or hoy
        
        dateDesde.setMaximumDate(hoy)
        dateDesde.setMinimumDate(fechaMin)

        dateHasta.setMaximumDate(hoy)
        dateHasta.setMinimumDate(fechaMin)
        
        # eventos para los botones
        btHoy.clicked.connect(self.hoy_handle)
        btSemana.clicked.connect(self.semana_handle)
        btMes.clicked.connect(self.mes_handle)
        
        self.hoy_handle()
    
    def hoy_handle(self):
        hoy = QDate.currentDate()
        self.dateDesde.setDate(hoy)
        self.dateHasta.setDate(hoy)
    
    def semana_handle(self):
        hoy = QDate.currentDate()
        current_day_of_week = hoy.dayOfWeek()
        
        start = hoy.addDays(-current_day_of_week)
        end = hoy.addDays(6 - current_day_of_week)
        
        self.dateDesde.setDate(start)
        self.dateHasta.setDate(end)
    
    def mes_handle(self):
        hoy = QDate.currentDate()
        
        start = QDate(hoy.year(), hoy.month(), 1)
        end = QDate(hoy.year(), hoy.month(), hoy.daysInMonth())
        
        self.dateDesde.setDate(start)
        self.dateHasta.setDate(end)


class InterfazFechasReportes(QObject):
    """ Interfaz para manejar widgets de fechas desde y hasta,
        por medio de botones de 'Hoy', 'Esta semana' y 'Este mes'. """
    
    def __init__(self, btQuincena: QPushButton,
                 btMes: QPushButton,
                 btAnio: QPushButton,
                 dateDesde: QDateEdit,
                 dateHasta: QDateEdit,
                 fechaMin: QDate = None):
        super().__init__(dateDesde)
        
        self.dateDesde = dateDesde
        self.dateHasta = dateHasta
        
        # configurar fechas permitidas
        hoy = QDate.currentDate()
        fechaMin = fechaMin or hoy
        
        dateDesde.setMaximumDate(hoy)
        dateDesde.setMinimumDate(fechaMin)
        
        dateHasta.setMaximumDate(hoy)
        dateHasta.setMinimumDate(fechaMin)
        
        # eventos para los botones
        btQuincena.clicked.connect(self.quincena_handle)
        btMes.clicked.connect(self.mes_handle)
        btAnio.clicked.connect(self.anio_handle)
        
        self.quincena_handle()
    
    def quincena_handle(self):
        hoy = QDate.currentDate()
        
        if hoy.day() <= 15:
            start = QDate(hoy.year(), hoy.month(), 1)
            end = QDate(hoy.year(), hoy.month(), 15)
        else:
            start = QDate(hoy.year(), hoy.month(), 16)
            end = QDate(hoy.year(), hoy.month(), hoy.daysInMonth())
        
        self.dateDesde.setDate(start)
        self.dateHasta.setDate(end)
    
    def mes_handle(self):
        hoy = QDate.currentDate()
        
        start = QDate(hoy.year(), hoy.month(), 1)
        end = QDate(hoy.year(), hoy.month(), hoy.daysInMonth())
        
        self.dateDesde.setDate(start)
        self.dateHasta.setDate(end)
    
    def anio_handle(self):
        hoy = QDate.currentDate()
        
        start = QDate(hoy.year(), 1, 1)
        end = QDate(hoy.year(), 12, 31)
        
        self.dateDesde.setDate(start)
        self.dateHasta.setDate(end)


class InterfazFiltro(QObject):
    """ Interfaz para manejar filtros de búsqueda.
    
        Recibe un widget QToolButton y una lista de opciones:
        nombre de opción, texto en placeholder e índice de columna asociada. """
    filtroCambiado = Signal(str)
    
    def __init__(self, button: QToolButton, options: list[tuple]):
        super().__init__(button)
        
        popup = QMenu(button)
        
        # primera opción y acción por defecto
        nombre, placeholder, idx = options[0]
        
        default = popup.addAction(
            nombre, lambda p=placeholder, i=idx: self.cambiar_filtro(p, i))
        button.clicked.connect(lambda p=placeholder, i=idx: self.cambiar_filtro(p, i))
        
        popup.setDefaultAction(default)
        self.filtro = idx
        
        # resto de acciones
        for nombre, placeholder, idx in options[1:]:
            popup.addAction(
                nombre, lambda p=placeholder, i=idx: self.cambiar_filtro(p, i))
        
        button.setMenu(popup)
    
    def cambiar_filtro(self, placeholder: str, idx: int):
        self.filtro = idx
        self.filtroCambiado.emit(placeholder)
