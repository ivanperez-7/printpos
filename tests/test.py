from backends.AdministrarVentas import App_TerminarVenta
from PrintPOS import app
import sql
from utils.mydataclasses import Usuario


con = sql.conectar_db('ivanperez', '123', 'Administrador')
user = Usuario.generarUsuarioActivo(sql.ManejadorUsuarios(con))

x = []

def crear(m):
    qdg = m(con, user)
    qdg.go_back.connect(qdg.close)
    x.append(qdg)
    qdg.show()

wdg = App_TerminarVenta(None, con, user, '725')
#wdg.go_back.connect(wdg.close)
wdg.show()
app.exec()
