domain = 'http://127.0.0.1:8000'

urls = {
    'login': f'{domain}/api/v1/token/',

    # Productos
    'get-tabla-precios-simples': f'{domain}/api/v1/productos/get-tabla-precios-simples/',

    # Ventas
    'get-usuario-pendientes': f'{domain}/api/v1/ventas/get-usuario-pendientes/',
}
