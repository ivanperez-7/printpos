""" Provee clases para enviar documentos PDF, en bytes, a impresoras. """

import io

from haps import Inject
import pymupdf
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QImage
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrinterInfo

from .generadores import generarOrdenCompra, generarCortePDF, generarTicketPDF
from config import INI
from interfaces import IWarningLogger
from sql import ManejadorVentas
from utils.mydecorators import run_in_thread
from utils.myutils import randFile


class ImpresoraPDF:
    """ Clase general para manejar impresoras y enviar archivos a estas. """

    warning_logger: IWarningLogger = Inject()

    def __init__(self, parent: QWidget = None):
        self.parent = parent
        self.printer = self.obtenerImpresora()

    def obtenerImpresora(self) -> QPrinter:
        return None

    def enviarAImpresora(self, data: io.BytesIO):
        """ Convertir PDF a imagen y mandar a impresora. """
        assert self.printer, 'Impresora aún no inicializada.'

        painter = QPainter()
        if not painter.begin(self.printer):
            raise RuntimeError(f"oops can't start {self.printer=}")

        doc = pymupdf.open(stream=data)
        for i, page in enumerate(doc):
            pix: pymupdf.Pixmap = page.get_pixmap(dpi=300, alpha=False)
            image = QImage(pix.samples, pix.w, pix.h, pix.stride, QImage.Format_RGB888)
            if INI.SAVE_PNG:
                image.save(randFile('jpg'))

            rect = painter.viewport()
            qtImageScaled = image.scaled(rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawImage(rect, qtImageScaled)

            if i < len(doc) - 1 and not self.printer.newPage():  # no se pudo crear nueva página
                print(f'Failed to create a new page for page {i + 2}')
                break
        painter.end()

    def __repr__(self):
        if self.printer is None:
            return 'Manejador de PDF sin impresora inicializada.'
        return f'Manejador de PDF con impresora {self.printer.printerName()}.'


class ImpresoraOrdenes(ImpresoraPDF):
    """ Impresora para órdenes de compra.
    Siempre crea diálogo para escoger impresora. """

    def obtenerImpresora(self):
        """ Diálogo para escoger impresora. En hilo principal. """
        printer = QPrinter(QPrinter.HighResolution)

        dialog = QPrintDialog(printer, self.parent)
        dialog.setOption(QPrintDialog.PrintToFile, False)
        dialog.setOption(QPrintDialog.PrintPageRange, False)

        if dialog.exec() != QPrintDialog.Accepted:
            return None
        else:
            return printer

    @run_in_thread
    def imprimirOrdenCompra(self, idx: int, manejador: ManejadorVentas = None):
        productos = manejador.obtenerTablaOrdenCompra(idx)
        total = manejador.obtenerImporteTotal(idx)
        anticipo = manejador.obtenerAnticipo(idx)
        nombre, telefono = manejador.obtenerClienteAsociado(idx)
        creacion, entrega = manejador.obtenerFechas(idx)

        data = generarOrdenCompra(productos, idx, nombre, telefono, total, anticipo, creacion, entrega)
        self.enviarAImpresora(data)


class ImpresoraTickets(ImpresoraPDF):
    """ Impresora para tickets.
    Intenta leer impresora por defecto del archivo config. """

    def obtenerImpresora(self):
        """ Lee impresora de tickets en archivo config. En hilo principal. """
        pInfo = QPrinterInfo.printerInfo(INI.IMPRESORA)

        if not pInfo.printerName():
            self.warning_logger.display(f'¡No se encontró la impresora {INI.IMPRESORA}!')
            return None
        else:
            return QPrinter(pInfo, QPrinter.HighResolution)

    @run_in_thread
    def imprimirTicketCompra(
        self, idx: int, nums: list[int] | slice = None, manejador: ManejadorVentas = None,
    ):
        """ Genera el ticket de compra a partir de un identificador en la base de datos.
        Recibe un arreglo de índices para imprimir pagos específicos. """
        # obtener datos de la compra, de la base de datos
        productos = list(manejador.obtenerTablaTicket(idx))

        # cambiar método de pago (abreviatura)
        abrev = {
            'Efectivo': 'EFEC',
            'Transferencia bancaria': 'TRF',
            'Tarjeta de crédito': 'TVP',
            'Tarjeta de débito': 'TVP',
        }

        pagos = manejador.obtenerPagosVenta(idx)

        if isinstance(nums, list):
            pagos = [pagos[i] for i in nums]
        elif isinstance(nums, slice):
            pagos = pagos[nums]

        for fecha, metodo, monto, pagado, vendedor in pagos:
            data = generarTicketPDF(productos, vendedor, idx, monto, pagado, abrev[metodo], fecha)
            self.enviarAImpresora(data)

    @run_in_thread
    def imprimirTicketPresupuesto(self, productos: list, vendedor: str):
        """ Genera un ticket para el presupuesto de una compra. """
        data = generarTicketPDF(productos, vendedor)
        self.enviarAImpresora(data)

    @run_in_thread
    def imprimirCorteCaja(self, caja, responsable: str):
        """ Genera un ticket para el presupuesto de una compra. """
        data = generarCortePDF(caja, responsable)
        self.enviarAImpresora(data)
