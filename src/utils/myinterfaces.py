""" Módulo para controladores de grupos de widgets y otras funciones. """

from PySide6.QtWidgets import (
    QPushButton,
    QDateEdit,
    QToolButton,
    QLineEdit,
    QMenu,
)
from PySide6.QtCore import QDate, QObject, Signal

from core import DateRange
from utils.mywidgets import TablaDatos

__all__ = ['InterfazPaginas', 'InterfazFechas', 'InterfazFiltro']


class InterfazPaginas(QObject):
    """ Interfaz para manejar paginados en tablas.

    Lo único que hace esta interfaz es manejar la propiedad
    `paginaActual` de la tabla asociada. """

    pagina_cambiada = Signal()

    def __init__(
        self,
        btAdelante: QPushButton,
        btUltimo: QPushButton,
        btAtras: QPushButton,
        btPrimero: QPushButton,
        tabla_display: TablaDatos,
    ):
        super().__init__(tabla_display)

        self.tabla = tabla_display

        btAdelante.clicked.connect(self.ir_adelante)
        btUltimo.clicked.connect(self.ir_ultimo)
        btAtras.clicked.connect(self.ir_atras)
        btPrimero.clicked.connect(self.ir_primero)

    def ir_adelante(self):
        self.tabla.paginaActual += 1
        self.pagina_cambiada.emit()

    def ir_ultimo(self):
        self.tabla.paginaActual = 1e6
        self.pagina_cambiada.emit()

    def ir_atras(self):
        self.tabla.paginaActual -= 1
        self.pagina_cambiada.emit()

    def ir_primero(self):
        self.tabla.paginaActual = 1
        self.pagina_cambiada.emit()


class InterfazFechas(QObject):
    """ Interfaz para manejar widgets de fechas desde y hasta,
    por medio de botones de 'Hoy', 'Esta semana' y 'Este mes'. """

    dateChanged = Signal()

    def __init__(
        self,
        btHoy: QPushButton,
        btSemana: QPushButton,
        btMes: QPushButton,
        dateDesde: QDateEdit,
        dateHasta: QDateEdit,
        fechaMin: QDate = None,
    ):
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

        emit = lambda: self.dateChanged.emit()
        dateDesde.dateChanged.connect(emit)
        dateHasta.dateChanged.connect(emit)

        self.hoy_handle()

    @property
    def rango_fechas(self):
        return DateRange(self.dateDesde.date(), self.dateHasta.date())

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

    def __init__(
        self,
        btQuincena: QPushButton,
        btMes: QPushButton,
        btAnio: QPushButton,
        dateDesde: QDateEdit,
        dateHasta: QDateEdit,
        fechaMin: QDate = None,
    ):
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

    cambiado = Signal()
    idx: int

    def __init__(self, button: QToolButton, search_bar: QLineEdit, options: list[tuple]):
        super().__init__(search_bar)

        self.search_bar = search_bar

        # primera opción y acción por defecto
        popup = QMenu(button)
        nombre, idx = options[0]

        call = lambda n=nombre, i=idx: self.cambiar_filtro(n, i)
        default = popup.addAction(nombre, call)
        button.clicked.connect(call)
        popup.setDefaultAction(default)

        self.idx = idx
        search_bar.setPlaceholderText(f'Buscar por {nombre.lower()}...')

        # resto de acciones
        for nombre, idx in options[1:]:
            popup.addAction(nombre, lambda n=nombre, i=idx: self.cambiar_filtro(n, i))

        button.setMenu(popup)

    def cambiar_filtro(self, nombre: str, idx: int):
        self.idx = idx
        self.search_bar.setPlaceholderText(f'Buscar por {nombre.lower() if nombre != "RFC" else nombre}...')
        self.cambiado.emit()
