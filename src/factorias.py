from interfaces import IModuloPrincipal


def crear_modulo(modulo: str) -> IModuloPrincipal:
    from backends.AdministrarClientes import App_AdministrarClientes
    from backends.AdministrarVentas import App_AdministrarVentas
    from backends.AdministrarInventario import App_AdministrarInventario
    from backends.AdministrarProductos import App_AdministrarProductos
    from backends.AdministrarUsuarios import App_AdministrarUsuarios
    from backends.Ajustes import App_Ajustes
    from backends.Caja import App_Caja
    from backends.CrearVenta import App_CrearVenta
    from backends.Login import App_Login
    from backends.Home import App_Home
    from backends.Reportes import App_Reportes

    modulos = {
        "App_AdministrarClientes": App_AdministrarClientes,
        "App_AdministrarVentas": App_AdministrarVentas,
        "App_AdministrarInventario": App_AdministrarInventario,
        "App_AdministrarProductos": App_AdministrarProductos,
        "App_AdministrarUsuarios": App_AdministrarUsuarios,
        "App_Ajustes": App_Ajustes,
        "App_Caja": App_Caja,
        "App_CrearVenta": App_CrearVenta,
        "App_Home": App_Home,
        "App_Login": App_Login,
        "App_Reportes": App_Reportes,
    }
    return modulos[modulo]()
