from functools import partial

from PySide6 import QtWidgets
from PySide6.QtGui import QFont
from PySide6.QtCharts import (
    QChart,
    QChartView,
    QBarSeries,
    QBarSet,
    QBarCategoryAxis,
    QPieSeries
)
from PySide6.QtCore import Qt, QDate, QModelIndex
from PySide6.QtGui import QPainter, QPen

from interfaces import IModuloPrincipal
from sql import ManejadorReportes, ManejadorVentas
from utils.myinterfaces import InterfazFechasReportes
from utils.myutils import stringify_float


class App_Reportes(QtWidgets.QWidget, IModuloPrincipal):
    """ Backend para la ventana de reportes varios. """

    def crear(self, conn, user):
        from ui.Ui_Reportes import Ui_Reportes

        self.ui = Ui_Reportes()
        self.ui.setupUi(self)

        self.conn = conn
        self.user = user

        for tbl in [self.ui.tableWidget,
                    self.ui.tableWidget_2,
                    self.ui.tableWidget_3,
                    self.ui.tabla_prods,
                    self.ui.tabla_intervalos]:
            tbl.setSortingEnabled(True)
            tbl.configurarCabecera(lambda col: col not in {0, 3, 4, 5},
                                   Qt.AlignCenter | Qt.TextWordWrap)
            tbl.tamanoCabecera(11)
            tbl.quitarBordeCabecera()

        for i, bt in enumerate([self.ui.btTablero,
                                self.ui.btVentas,
                                self.ui.btVendedores,
                                self.ui.btClientes,
                                self.ui.btProductos]):
            bt.clicked.connect(partial(self.ui.stackedWidget.setCurrentIndex, i))

        # fechas por defecto
        manejador = ManejadorVentas(self.conn)
        fechaMin = manejador.obtenerFechaPrimeraVenta()

        InterfazFechasReportes(
            self.ui.btQuincena, self.ui.btMes, self.ui.btAnio,
            self.ui.dateDesde, self.ui.dateHasta, fechaMin)

        self.ui.btRegresar.clicked.connect(self.go_back.emit)
        self.ui.stackedWidget.currentChanged.connect(self.actualizar_widget_activo)
        self.ui.dateHasta.dateChanged.connect(self.actualizar_widget_activo)
        self.ui.dateDesde.dateChanged.connect(self.actualizar_widget_activo)

    def showEvent(self, event):
        self.actualizar_widget_activo()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @property
    def fechaDesde(self):
        return self.ui.dateDesde.date()

    @property
    def fechaHasta(self):
        return self.ui.dateHasta.date()

    def actualizar_widget_activo(self):
        funcs = [
            self.actualizar_tablero,
            self.actualizar_tablero,
            self.actualizar_vendedores,
            self.actualizar_clientes,
            self.actualizar_productos
        ]
        idx = self.ui.stackedWidget.currentIndex()
        funcs[idx]()

    # ************************************************ #
    def actualizar_tablero(self):
        # alimentar QLabels
        man = ManejadorReportes(self.conn)
        brutos, num_ventas = man.obtenerIngresosBrutos()
        self.ui.lbIngresosBrutos.setText('${:,.2f}'.format(brutos))
        self.ui.lbCountVentas.setText('a través de {:,d} ventas'.format(num_ventas))

        vendedor, cantidad = man.obtenerTopVendedor()
        self.ui.lbVendedorBrutos.setText(vendedor)
        self.ui.lbVendedorTotal.setText('${:,.2f}'.format(cantidad))

        abreviado, codigo, count = man.obtenerTopProducto()
        self.ui.lbProdVendidos.setText(codigo)
        self.ui.lbProdCount.setText(stringify_float(count) + ' unidades')

        # gráficas 
        self.ui.bar_ventas.alimentar_datos(self.conn)
        self.ui.pie_prods.alimentar_productos(self.conn)
        self.ui.pie_metodos.alimentar_metodos(self.conn)

    def actualizar_clientes(self):
        man = ManejadorReportes(self.conn)
        tabla = self.ui.tableWidget_3
        tabla.llenar(man.obtenerReporteClientes(self.fechaDesde, self.fechaHasta))
        tabla.resizeRowsToContents()

    def actualizar_vendedores(self):
        def handle(index: QModelIndex):
            nombre = index.siblingAtColumn(0).data()
            self.ui.vend_w_graph.alimentar_vendedor(self.conn, nombre)

        man = ManejadorReportes(self.conn)
        tabla = self.ui.tableWidget_2
        tabla.llenar(man.obtenerReporteVendedores(self.fechaDesde, self.fechaHasta))
        tabla.resizeRowsToContents()
        tabla.clicked.connect(handle)

    def actualizar_productos(self):
        tabla_intervalos = self.ui.tabla_intervalos
        tabla_intervalos.modelo = tabla_intervalos.Modelos.CREAR_VENTA
        tabla_intervalos.configurarCabecera(lambda col: col == 0)
        tabla_intervalos.setSortingEnabled(False)

        def handle(index: QModelIndex):
            codigo = index.siblingAtColumn(1).data()
            self.ui.ventas_prod_graph.alimentar_producto(self.conn, codigo)
            tabla_intervalos.llenar(man.obtenerVentasIntervalos(codigo, self.fechaDesde, self.fechaHasta))

        man = ManejadorReportes(self.conn)
        tabla = self.ui.tabla_prods
        tabla.llenar(man.obtenerReporteProductos(self.fechaDesde, self.fechaHasta))
        tabla.resizeRowsToContents()
        tabla.clicked.connect(handle)


#########################################
# WIDGETS PERSONALIZADOS PARA EL MÓDULO #
#########################################
class ChartView(QChartView):
    def __init__(self, parent=None):
        super().__init__(parent)

        font = QFont()
        font.setPointSize(11)

        self.setFont(font)
        self.setRenderHint(QPainter.Antialiasing)

    def alimentar_datos(self, conn):
        chart = QChart()
        series = QBarSeries()
        set0 = QBarSet("Ventas brutas")

        # Replace this with your sales data for each month
        man = ManejadorReportes(conn)
        current_year = QDate.currentDate().year()
        data = man.obtenerGraficaVentas(current_year)

        month_labels = []

        for anio_mes, total, num_ventas in data:
            set0.append(total)
            month_labels.append(anio_mes)

        series.append(set0)
        chart.addSeries(series)

        chart.setTitle(f"Ventas por mes del año {current_year}")
        chart.setFont(self.font())
        chart.setTitleFont(self.font())
        chart.setAnimationOptions(QChart.AllAnimations)

        categories_axis = QBarCategoryAxis()
        categories_axis.append(month_labels)
        chart.createDefaultAxes()
        chart.setAxisX(categories_axis, series)

        chart.layout().setContentsMargins(0, 0, 0, 0);
        chart.setBackgroundRoundness(0);
        self.setChart(chart)

    def alimentar_vendedor(self, conn, vendedor: str):
        chart = QChart()
        series = QBarSeries()
        set0 = QBarSet("Ventas brutas")

        # Replace this with your sales data for each month
        man = ManejadorReportes(conn)
        current_year = QDate.currentDate().year()
        data = man.obtenerGraficaVentasVendedor(vendedor, current_year)

        month_labels = []

        for anio_mes, total in data:
            set0.append(total)
            month_labels.append(anio_mes)

        series.append(set0)
        chart.addSeries(series)

        chart.setTitle(f"Ventas de {vendedor} en el año {current_year}")
        chart.setFont(self.font())
        chart.setTitleFont(self.font())
        chart.setAnimationOptions(QChart.AllAnimations)

        categories_axis = QBarCategoryAxis()
        categories_axis.append(month_labels)
        chart.createDefaultAxes()
        chart.setAxisX(categories_axis, series)

        chart.layout().setContentsMargins(0, 0, 0, 0);
        chart.setBackgroundRoundness(0);
        self.setChart(chart)

    def alimentar_producto(self, conn, codigo: str):
        chart = QChart()
        series = QBarSeries()
        set0 = QBarSet("Ventas brutas")

        # Replace this with your sales data for each month
        man = ManejadorReportes(conn)
        current_year = QDate.currentDate().year()
        data = man.obtenerGraficaVentasProducto(codigo, current_year)

        month_labels = []

        for anio_mes, total in data:
            set0.append(total)
            month_labels.append(anio_mes)

        series.append(set0)
        chart.addSeries(series)

        chart.setTitle(f"Ventas de {codigo} en el año {current_year}")
        chart.setFont(self.font())
        chart.setTitleFont(self.font())
        chart.setAnimationOptions(QChart.AllAnimations)

        categories_axis = QBarCategoryAxis()
        categories_axis.append(month_labels)
        chart.createDefaultAxes()
        chart.setAxisX(categories_axis, series)

        chart.layout().setContentsMargins(0, 0, 0, 0);
        chart.setBackgroundRoundness(0);
        self.setChart(chart)


class ChartView2(QChartView):
    def __init__(self, parent=None):
        super().__init__(parent)

        font = QFont()
        font.setPointSize(11)

        self.setFont(font)
        self.setRenderHint(QPainter.Antialiasing)

    def alimentar_productos(self, conn):
        man = ManejadorReportes(conn)
        series = QPieSeries()

        for abrev, codigo, num in man.obtenerTopProducto(6)[1:]:
            s = series.append(codigo + ' ({})'.format(stringify_float(num)), num)
            s.hovered.connect(partial(self.handle_slice_hover, s))

        if not series.slices():
            return
        _slice = max(series.slices(), key=lambda s: s.value())
        _slice.setLabelVisible(True)
        _slice.setPen(QPen(Qt.darkGreen, 2))
        _slice.setBrush(Qt.green)
        _slice.hovered.disconnect()
        _slice.hovered.connect(partial(self.handle_max_hover, _slice))

        chart = QChart()
        chart.setFont(self.font())
        chart.setTitleFont(self.font())
        chart.addSeries(series)
        chart.setTitle('Los otros productos más vendidos')
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().hide()

        chart.layout().setContentsMargins(0, 0, 0, 0);
        chart.setBackgroundRoundness(0);
        self.setChart(chart)

    def alimentar_metodos(self, conn):
        man = ManejadorReportes(conn)
        series = QPieSeries()

        for metodo, num in man.obtenerGraficaMetodos():
            s = series.append(metodo + ' ({})'.format(num), num)
            s.hovered.connect(partial(self.handle_slice_hover, s))

        _slice = max(series.slices(), key=lambda s: s.value())
        _slice.setLabelVisible(True)
        _slice.setPen(QPen(Qt.darkBlue, 2))
        _slice.setBrush(Qt.blue)
        _slice.hovered.disconnect()
        _slice.hovered.connect(partial(self.handle_max_hover, _slice))

        chart = QChart()
        chart.setFont(self.font())
        chart.setTitleFont(self.font())
        chart.addSeries(series)
        chart.setTitle('Métodos de pago más usados')
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().hide()

        chart.layout().setContentsMargins(0, 0, 0, 0);
        chart.setBackgroundRoundness(0);
        self.setChart(chart)

    def handle_slice_hover(self, _slice, state):
        _slice.setExploded(state)
        _slice.setLabelVisible(state)

    def handle_max_hover(self, _slice, state):
        _slice.setExploded(state)
