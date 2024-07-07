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
        
        printer = ImpresoraTickets()
        man = sql.ManejadorVentas(sql.conectar_firebird('ivanperez', '123', 'administrador'))
        self.assertEqual(printer.printer.printerName(), INI.IMPRESORA)
        
        res1 = printer.imprimirTicketCompra(670, manejador=man) # varios pagos
        QThreadPool.globalInstance().waitForDone()  # <- porque las impresoras usan run_in_thread
        res2 = printer.imprimirTicketCompra(671, manejador=man) # un solo pago
        QThreadPool.globalInstance().waitForDone()  # <- porque las impresoras usan run_in_thread
        res3 = printer.imprimirTicketCompra(670, [0,2], manejador=man) # varios pagos, pero seleccionados
        QThreadPool.globalInstance().waitForDone()  # <- porque las impresoras usan run_in_thread
        
        prods = [ItemVenta(1, 'IMP B/N 1', 'Impresión ByN', 0.7, 0., random.randint(10, 200), '', False)]
        res4 = printer.imprimirTicketPresupuesto(prods*3, 'yo merengues')
        
        caja = Caja([
            (datetime.now(), 500., 'renta lol', 'Efectivo', 'ivan p.'),
            (datetime.now(), -40., 'pago', 'Tarjeta de débito', 'ivan p.')
        ])
        res5 = printer.imprimirCorteCaja(caja, 'io menregues')
        
        QThreadPool.globalInstance().waitForDone()  # <- porque las impresoras usan run_in_thread
    
    def test_async_pdf_printer_ordenes(self):
        printer = ImpresoraOrdenes()
        self.assertEqual(printer.printer.printerName(), INI.IMPRESORA)
        
        res1 = printer.imprimirOrdenCompra(693, manejador=sql.ManejadorVentas(sql.conectar_firebird('ivanperez', '123', 'administrador')))
        QThreadPool.globalInstance().waitForDone()  # <- porque las impresoras usan run_in_thread


if __name__ == '__main__':
    main()
