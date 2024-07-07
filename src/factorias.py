from interfaces import IModuloPrincipal


def crear_modulo(modulo: str) -> IModuloPrincipal:
    match modulo:
        case 'App_AdministrarClientes':
            from backends.AdministrarClientes import App_AdministrarClientes
            return App_AdministrarClientes()
        
        case 'App_AdministrarVentas':
            from backends.AdministrarVentas import App_AdministrarVentas
            return App_AdministrarVentas()
        
        case 'App_AdministrarInventario':
            from backends.AdministrarInventario import App_AdministrarInventario
            return App_AdministrarInventario()
        
        case 'App_AdministrarProductos':
            from backends.AdministrarProductos import App_AdministrarProductos
            return App_AdministrarProductos()
        
        case 'App_AdministrarUsuarios':
            from backends.AdministrarUsuarios import App_AdministrarUsuarios
            return App_AdministrarUsuarios()
        
        case 'App_Ajustes':
            from backends.Ajustes import App_Ajustes
            return App_Ajustes()
        
        case 'App_Caja':
            from backends.Caja import App_Caja
            return App_Caja()
        
        case 'App_CrearVenta':
            from backends.CrearVenta import App_CrearVenta
            return App_CrearVenta()
        
        case 'App_Login':
            from backends.Login import App_Login
            return App_Login()
        
        case 'App_Home':
            from backends.Home import App_Home
            return App_Home()
        
        case 'App_Reportes':
            from backends.Reportes import App_Reportes
            return App_Reportes()
        
        case _:
            raise RuntimeError('No existe el módulo ' + modulo)
