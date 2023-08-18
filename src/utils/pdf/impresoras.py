""" Provee clases para enviar documentos PDF, en bytes, a impresoras. """
import io
from functools import wraps
from typing import overload

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QImage
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrinterInfo

from Caja import Caja
from Login import Usuario
from utils.mydecorators import run_in_thread
from utils.myutils import leer_config
from utils.pdf.generadores import _generarCortePDF, _generarOrdenCompra, _generarTicketPDF
from utils import sql


def verificar_impresora(func):
    """ Simple decorador que verifica si existe atributo `printer`. """
    @wraps(func)
    def wrapped(*args, **kwargs):
        cls: ImpresoraPDF = args[0]
        if cls.printer:
            func(*args, **kwargs)
    return wrapped


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
        return printer
    
    @staticmethod
    def obtenerImpresoraTickets():
        """ Lee impresora de tickets en archivo config. En hilo principal. """
        from utils.mywidgets import WarningDialog
        
        config = leer_config()
        printerName = config['IMPRESORAS']['default']
        
        pInfo = QPrinterInfo.printerInfo(printerName)
        if not pInfo.printerName():
            WarningDialog(f'¡No se encontró la impresora {printerName}!')
            return None
        
        return QPrinter(pInfo, QPrinter.HighResolution)
    
    def enviarAImpresora(self, data: io.BytesIO):
        """ Convertir PDF a imagen y mandar a impresora. """
        import fitz
        
        doc = fitz.open(stream=data)
        painter = QPainter()
        if not painter.begin(self.printer):
            return
        
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=300, alpha=False)
            image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            # image.save(f'out{i}.jpg')
            
            rect = painter.viewport()
            qtImageScaled = image.scaled(rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawImage(rect, qtImageScaled)
            
            if i > 0:
                self.printer.newPage()
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
    
    @verificar_impresora
    @run_in_thread
    def imprimirOrdenCompra(self, idx: int):
        manejador = sql.ManejadorVentas(self.conn)
        data = _generarOrdenCompra(manejador, idx)
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
    
    @verificar_impresora
    @run_in_thread
    def imprimirTicketCompra(self, idx):
        """ Genera el ticket de compra a partir de un identificador en la base de datos. """
        # obtener datos de la compra, de la base de datos
        manejador = sql.ManejadorVentas(self.conn)
        productos = manejador.obtenerTablaTicket(idx)
        
        # más datos para el ticket
        vendedor = manejador.obtenerUsuarioAsociado(idx)
        fechaCreacion, _ = manejador.obtenerFechas(idx)
        
        # cambiar método de pago (abreviatura)
        abrev = {'Efectivo': 'EFEC',
                 'Transferencia bancaria': 'TRF',
                 'Tarjeta de crédito': 'TVP',
                 'Tarjeta de débito': 'TVP'}
        
        for metodo, monto, pagado in manejador.obtenerPagosVenta(idx):
            data = _generarTicketPDF(idx, productos, vendedor, monto,
                                     pagado, abrev[metodo], fechaCreacion)
            self.enviarAImpresora(data)
    
    @verificar_impresora
    @run_in_thread
    def imprimirTicketPresupuesto(self, productos: list[tuple], vendedor: str):
        """ Genera un ticket para el presupuesto de una compra. """
        data = _generarTicketPDF(0, productos, vendedor)
        self.enviarAImpresora(data)
    
    @verificar_impresora
    @run_in_thread
    def imprimirCorteCaja(self, caja: Caja, user: Usuario):
        """ Genera un ticket para el presupuesto de una compra. """
        data = _generarCortePDF(caja, user)
        self.enviarAImpresora(data)
