from PySide6.QtCore import QDateTime, QDate, QTime

from backends.CrearVenta import App_ConfirmarVenta, App_CrearVenta, App_FechaEntrega
from backends.AdministrarVentas import App_DetallesVenta, App_ImprimirTickets
from PrintPOS import app
import sql
from utils.mydataclasses import Usuario, Venta, ItemVenta


con = sql.conectar_db('pablo', '1', 'vendedor')
user = Usuario.generarUsuarioActivo(sql.ManejadorUsuarios(con))



venta = Venta()
venta.agregarProducto(
    ItemVenta(1, 'IMP B/N 1', 'Impresión ByN', 0.7, 0., 500, '', False))
venta.fechaEntrega = QDateTime(QDate(2024, 6, 22), QTime(13, 23, 2))
venta.metodo_pago = 'Transferencia bancaria'
venta.id_cliente = 2


wdg = App_ConfirmarVenta(venta, con, user)
wdg.success.connect(wdg.close)
wdg.show()
"""
wdg = App_CrearVenta(con, user)
wdg.go_back.connect(wdg.close)
wdg = App_FechaEntrega(venta.fechaEntrega)
wdg.success.connect(print)
wdg.show()
"""

#wdg = App_ImprimirTickets(786, con)
#wdg.show()

app.exec()
