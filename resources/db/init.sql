-- deshabilitar temporalmente las restricciones de llaves foráneas
PRAGMA foreign_keys = 0;

DELETE FROM ProductosUtilizaInventario;
DELETE FROM Clientes;
DELETE FROM Ventas;
DELETE FROM Usuarios WHERE idUsuarios != 1;
DELETE FROM Inventario;
DELETE FROM Productos;
DELETE FROM Caja;
DELETE FROM VentasDetallado;
DELETE FROM sqlite_sequence;

-- reactivar las restricciones de llaves foráneas
PRAGMA foreign_keys = 1;

-- insertar cliente 'Público general'
INSERT INTO Clientes (
	nombre, telefono, whatsapp, correo,
	direccion, RFC, clienteEspecial, descuentos
)
VALUES
	('Público general', 'N/A', 'N/A', 'N/A',
	'N/A', 'N/A', 0, '')
