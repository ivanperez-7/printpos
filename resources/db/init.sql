INSERT INTO CLIENTES (
    NOMBRE, TELEFONO, CORREO, DIRECCION,
    RFC, CLIENTE_ESPECIAL, DESCUENTOS
)
VALUES 
    ('P�blico general', 'N/A', 'N/A', 'N/A', 'N/A', false, '');

INSERT INTO USUARIOS (
    USUARIO, NOMBRE, PERMISOS
)
VALUES
    ('SYSDBA', 'Administrador DB', 'Administrador');