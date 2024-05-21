""" Provee clases para enviar documentos PDF, en bytes, a impresoras. """
import io
from typing import overload

import fitz
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QImage
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrinterInfo

from backends.Caja import Caja
from config import INI
from utils.mydecorators import run_in_thread
from utils.myutils import *
from utils.mywidgets import WarningDialog
from utils.pdf.generadores import *
from utils import sql


class ImpresoraPDF:
    """ Clase general para manejar impresoras y enviar archivos a estas. """
    
    def __init__(self):
        self.printer: QPrinter = None
    
    @staticmethod
    def escogerImpresora(parent: QWidget = None):
        """ Diálogo para escoger impresora. En hilo principal. """
        printer = QPrinter(QPrinter.HighResolution)
        
        dialog = QPrintDialog(printer, parent)
        opts = QPrintDialog.PrintDialogOption
        dialog.setOption(opts.PrintToFile, False)
        dialog.setOption(opts.PrintPageRange, False)
        
        if dialog.exec() != QPrintDialog.Accepted:
            return None
        else:
            return printer
    
    @staticmethod
    def obtenerImpresoraTickets():
        """ Lee impresora de tickets en archivo config. En hilo principal. """
        pInfo = QPrinterInfo.printerInfo(INI.IMPRESORA)
        if not pInfo.printerName():
            WarningDialog(f'¡No se encontró la impresora {INI.IMPRESORA}!')
            return None
        else:
            return QPrinter(pInfo, QPrinter.HighResolution)
    
    def enviarAImpresora(self, data: io.BytesIO):
        """ Convertir PDF a imagen y mandar a impresora. """
        doc = fitz.open(stream=data)
        painter = QPainter()
        
        if not painter.begin(self.printer):
            return
        
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=300, alpha=False)
            image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            #image.save(randFile('jpg'))
            
            rect = painter.viewport()
            qtImageScaled = image.scaled(rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawImage(rect, qtImageScaled)
            
            if i < len(doc) - 1 and not self.printer.newPage():   # no se pudo crear nueva página
                print(f"Failed to create a new page for page {i + 2}")
                break
        painter.end()
    
    def __repr__(self):
        if self.printer is None:
            return 'Manejador de PDF sin impresora inicializada.'
        return f'Manejador de PDF con impresora {self.printer.printerName()}.'


class ImpresoraOrdenes(ImpresoraPDF):
    """ Impresora para órdenes de compra. 
        Siempre crea diálogo para escoger impresora. """
    
    @overload
    def __init__(self, conn: sql.Connection) -> None: ...
    @overload
    def __init__(self, parent: QWidget) -> None: ...
    
    def __init__(self, arg):
        super().__init__()
        if isinstance(arg, sql.Connection):
            self.conn = arg
            self.parent = None
        elif isinstance(arg, QWidget):
            self.conn = arg.conn
            self.parent = arg
        else:
            raise ValueError('Argumentos inválidos: ninguna implementación.')
        self.printer = self.escogerImpresora(self.parent)
    
    @run_in_thread
    def imprimirOrdenCompra(self, idx: int):
        assert self.printer, 'Impresora aún no inicializada.'
        
        manejador = sql.ManejadorVentas(self.conn)
        data = generarOrdenCompra(manejador, idx)
        self.enviarAImpresora(data)


class ImpresoraTickets(ImpresoraPDF):
    """ Impresora para tickets. 
        Intenta leer impresora por defecto del archivo config. """
    
    @overload
    def __init__(self, conn: sql.Connection) -> None: ...
    @overload
    def __init__(self, parent: QWidget) -> None: ...
    
    def __init__(self, arg):
        super().__init__()
        if isinstance(arg, sql.Connection):
            self.conn = arg
        elif isinstance(arg, QWidget):
            self.conn = arg.conn
        else:
            raise ValueError('Argumentos inválidos: ninguna implementación.')
        self.printer = self.obtenerImpresoraTickets()
    
    @run_in_thread
    def imprimirTicketCompra(self, idx: int, nums: list[int] = None):
        """ Genera el ticket de compra a partir de un identificador en la base de datos.
            Recibe un arreglo de índices para imprimir pagos específicos. """
        assert self.printer, 'Impresora aún no inicializada.'
        # obtener datos de la compra, de la base de datos
        manejador = sql.ManejadorVentas(self.conn)
        productos = list(manejador.obtenerTablaTicket(idx))
        
        # más datos para el ticket
        vendedor = manejador.obtenerUsuarioAsociado(idx)
        
        # cambiar método de pago (abreviatura)
        abrev = {'Efectivo': 'EFEC',
                 'Transferencia bancaria': 'TRF',
                 'Tarjeta de crédito': 'TVP',
                 'Tarjeta de débito': 'TVP'}
        
        pagos = manejador.obtenerPagosVenta(idx)
        
        if nums is not None:   # determinados pagos
            pagos = [pagos[i] for i in nums]
        
        for fecha, metodo, monto, pagado in pagos:
            data = generarTicketPDF(productos, vendedor, idx, monto,
                                    pagado, abrev[metodo], fecha)
            self.enviarAImpresora(data)
    
    @run_in_thread
    def imprimirTicketPresupuesto(self, productos: list, vendedor: str):
        """ Genera un ticket para el presupuesto de una compra. """
        assert self.printer, 'Impresora aún no inicializada.'
        
        data = generarTicketPDF(productos, vendedor)
        self.enviarAImpresora(data)
    
    @run_in_thread
    def imprimirCorteCaja(self, caja: Caja, responsable: str):
        """ Genera un ticket para el presupuesto de una compra. """
        assert self.printer, 'Impresora aún no inicializada.'
        
        data = generarCortePDF(caja, responsable)
        self.enviarAImpresora(data)
