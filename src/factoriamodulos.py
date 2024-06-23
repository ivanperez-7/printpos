from injector import Injector

from sql.core import Connection, conectar_db, DatabaseManager
from utils.mydataclasses import Usuario


def _configure(binder):
    binder.bind(Connection, to=(con := conectar_db('ivanperez', '123', 'vendedor')))
    binder.bind(Usuario, to=Usuario.generarUsuarioActivo(DatabaseManager(con)))
_modulo_injector = Injector(_configure)


class FactoriaModulosPrincipales:
    def crear_modulo(self, modulo: str):
        match modulo:
            case 'App_AdministrarClientes':
                from backends.AdministrarClientes import App_AdministrarClientes
                return _modulo_injector.get(App_AdministrarClientes)
            
            case 'App_AdministrarVentas':
                from backends.AdministrarVentas import App_AdministrarVentas
                return _modulo_injector.get(App_AdministrarVentas)
            
            case 'App_AdministrarInventario':
                from backends.AdministrarInventario import App_AdministrarInventario
                return _modulo_injector.get(App_AdministrarInventario)
            
            case 'App_AdministrarProductos':
                from backends.AdministrarProductos import App_AdministrarProductos
                return _modulo_injector.get(App_AdministrarProductos)
            
            case 'App_AdministrarUsuarios':
                from backends.AdministrarUsuarios import App_AdministrarUsuarios
                return _modulo_injector.get(App_AdministrarUsuarios)
            
            case 'App_Ajustes':
                from backends.Ajustes import App_Ajustes
                return _modulo_injector.get(App_Ajustes)
            
            case 'App_Caja':
                from backends.Caja import App_Caja
                return _modulo_injector.get(App_Caja)
            
            case 'App_CrearVenta':
                from backends.CrearVenta import App_CrearVenta
                return _modulo_injector.get(App_CrearVenta)
            
            case 'App_Home':
                from backends.Home import App_Home
                return _modulo_injector.get(App_Home)
            
            case 'App_Reportes':
                from backends.Reportes import App_Reportes
                return _modulo_injector.get(App_Reportes)
