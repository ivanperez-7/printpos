from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from backends.shared_widgets import Base_VisualizarProductos


class App_ConsultarPrecios(Base_VisualizarProductos):
    """Backend para el módulo de consultar precios.
    No se puede cerrar hasta cerrar por completo el sistema."""

    def __init__(self, conn):
        super().__init__(conn)

        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint)
        self.setWindowTitle("Consultar precios")
        self.setWindowIcon(QIcon(":img/icon.ico"))

        self.warnings = False

        self.ui.label.setText("Consultar precios")
        self.ui.btRegresar.setCursor(Qt.CursorShape.ArrowCursor)
        self.ui.btRegresar.setIcon(QIcon(":/img/resources/images/package.png"))

        self.ui.btAgregar.hide()
        self.ui.groupBoxEspecGran.hide()
        self.ui.groupBoxEspecSimple.hide()

        # eventos para tabla de productos simples
        self.ui.tabla_seleccionar.itemClicked.connect(self.mostrarSimple)
        self.ui.txtCantidad.textChanged.connect(self.mostrarSimple)
        self.ui.checkDuplex.toggled.connect(self.mostrarSimple)

        # eventos para tabla de gran formato
        self.ui.tabla_granformato.itemClicked.connect(self.medidasHandle)
        self.ui.txtAnchoMaterial.textChanged.connect(self.medidasHandle)
        self.ui.txtAltoMaterial.textChanged.connect(self.medidasHandle)
        # lo demás está en la superclase :p

        self.showMinimized()

    def closeEvent(self, event):
        if event.spontaneous():
            event.ignore()
        else:
            super().closeEvent(event)

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def mostrarSimple(self):
        if item := self.generarSimple():
            self.ui.lbTotalSimple.setText(f"Total: ${item.importe:,.2f}")
        else:
            self.ui.lbTotalSimple.setText("Total: ...")

    def medidasHandle(self):
        if item := self.generarGranFormato():
            self.ui.lbTotalGran.setText(f"Total: ${item.importe:,.2f}")
        else:
            self.ui.lbTotalGran.setText("Total: ...")
