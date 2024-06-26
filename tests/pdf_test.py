from datetime import datetime
import random
from unittest import TestCase, main, mock

from PySide6.QtCore import QThreadPool
from ui import resources_rc

from config import INI
from pdf import ImpresoraOrdenes, ImpresoraTickets
import PrintPOS
import sql


class PdfTests(TestCase):
    def test_async_pdf_printer_tickets(self):
        from utils.mydataclasses import Caja, ItemVenta
        
        printer = ImpresoraTickets(sql.conectar_db('ivanperez', '123', 'administrador'))
        self.assertEqual(printer.printer.printerName(), INI.IMPRESORA)
        
        res1 = printer.imprimirTicketCompra(776) # varios pagos
        res2 = printer.imprimirTicketCompra(676) # un solo pago
        res3 = printer.imprimirTicketCompra(776, [0,2]) # varios pagos, pero seleccionados
        
        prods = [ItemVenta(1, 'IMP B/N 1', 'Impresión ByN', 0.7, 0., random.randint(10, 200), '', False)]
        res4 = printer.imprimirTicketPresupuesto(prods, 'yo merengues')
        
        caja = Caja([
            (datetime.now(), 500., 'renta lol', 'Efectivo', 'ivan p.'),
            (datetime.now(), -40., 'pago', 'Tarjeta de débito', 'ivan p.')
        ])
        res5 = printer.imprimirCorteCaja(caja, 'io menregues')
        
        QThreadPool.globalInstance().waitForDone()  # <- porque las impresoras usan run_in_thread
    
    def test_async_pdf_printer_ordenes(self):
        printer = ImpresoraOrdenes(sql.conectar_db('ivanperez', '123', 'administrador'))
        self.assertEqual(printer.printer.printerName(), INI.IMPRESORA)
        
        res1 = printer.imprimirOrdenCompra(676)
        QThreadPool.globalInstance().waitForDone()  # <- porque las impresoras usan run_in_thread


if __name__ == '__main__':
    main()
