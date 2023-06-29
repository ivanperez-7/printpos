INSERT INTO CLIENTES (
    NOMBRE, TELEFONO, CORREO, DIRECCION,
    RFC, CLIENTEESPECIAL, DESCUENTOS
)
VALUES 
    ('Público general', 'N/A', 'N/A', 'N/A', 'N/A', false, '');

INSERT INTO USUARIOS (
    USUARIO, NOMBRE, PERMISOS
)
VALUES
    ('SYSDBA', 'Administrador DB', 'Administrador');