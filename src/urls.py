domain = 'http://127.0.0.1:8000'

urls = {
    'login': f'{domain}/api/v1/token/',

    # Clientes
    'clientes': f'{domain}/api/v1/clientes/',

    # Productos
    'productos': f'{domain}/api/v1/productos/productos/',
    'inventario': f'{domain}/api/v1/productos/inventario/',

    # Ventas
    'get-usuario-pendientes': f'{domain}/api/v1/ventas/get-usuario-pendientes/',
}
