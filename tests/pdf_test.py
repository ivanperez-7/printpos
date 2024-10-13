from datetime import datetime
import io
import unittest

from reportlab.pdfgen import canvas

from pdf.generadores import generarOrdenCompra, generarTicketPDF, generarCortePDF
from pdf.impresoras import ImpresoraPDF, ImpresoraTickets, ImpresoraOrdenes
import PrintPOS
from utils.mydataclasses import ItemVenta, Caja
from ui import resources_rc


class TestPDFGenerators(unittest.TestCase):
    def setUp(self):
        self.folio = 1
        self.nombre = 'John Doe'
        self.telefono = '1234567890'
        self.total = 50.0  # Assuming Moneda is handled properly
        self.anticipo = 5.0  # Assuming Moneda is handled properly
        self.fecha_creacion = datetime.now()
        self.fecha_entrega = datetime.now()

    def test_generarOrdenCompra(self):
        productos = [
            (15, 'Product A', 'Spec A', 10.0, 0.0),
            (15, 'Product B', 'Spec B', 20.0, 0.0),
        ]
        pdf_bytes = generarOrdenCompra(
            productos,
            self.folio,
            self.nombre,
            self.telefono,
            self.total,
            self.anticipo,
            self.fecha_creacion,
            self.fecha_entrega,
        )
        self.assertGreater(pdf_bytes.getbuffer().nbytes, 0, 'PDF should not be empty')

    def test_generarTicketPDF(self):
        productos = [ItemVenta(1, 'Product A', 'Spec A', 10.0, 0, 15, '')]
        pdf_bytes = generarTicketPDF(
            productos,
            vendedor='Jane Doe',
            folio=self.folio,
            total=self.total,
            recibido=10.0,
            metodo_pago='EFEC',
            fecha_creacion=self.fecha_creacion,
        )
        self.assertGreater(pdf_bytes.getbuffer().nbytes, 0, 'PDF should not be empty')

    def test_generarCortePDF(self):
        caja = Caja()  # Mock or create an instance of Caja as needed
        pdf_bytes = generarCortePDF(caja, responsable='Manager')
        self.assertGreater(pdf_bytes.getbuffer().nbytes, 0, 'PDF should not be empty')


class TestPDFPrinters(unittest.TestCase):
    def setUp(self):
        self.impresora_ordenes = ImpresoraOrdenes()
        self.impresora_tickets = ImpresoraTickets()

    def create_dummy_pdf(self):
        """Create a simple PDF in memory for testing."""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)
        c.drawString(100, 750, 'This is a test PDF.')
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    def test_obtenerImpresora_ordenes(self):
        printer = self.impresora_ordenes.obtenerImpresora()
        self.assertIsNotNone(printer, 'Impresora for orders should not be None')

    def test_obtenerImpresora_tickets(self):
        printer = self.impresora_tickets.obtenerImpresora()
        self.assertIsNotNone(printer, 'Impresora for tickets should not be None')

    def test_enviarAImpresora(self):
        # Create a dummy PDF byte stream for testing
        dummy_pdf = self.create_dummy_pdf()
        try:
            self.impresora_ordenes.enviarAImpresora(dummy_pdf)
            # If no exception, it should be fine
            self.assertTrue(True)
        except Exception as e:
            self.fail(f'Sending to printer failed with exception: {e}')


if __name__ == '__main__':
    unittest.main()
