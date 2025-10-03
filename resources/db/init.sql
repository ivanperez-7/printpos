
/********************* VIEWS **********************/

CREATE VIEW MOVIMIENTOS_CAJA (FECHA_HORA, MONTO, DESCRIPCION, METODO, NOMBRE)
AS SELECT  * FROM (
    SELECT  fecha_hora,
            monto,
            TRIM(IIF(monto > 0, 'Pago', 'Devolución'))
                || ' de venta con folio ' || VP.id_ventas AS descripcion,
            MP.metodo,
            U.nombre
    FROM    ventas_pagos VP
            LEFT JOIN metodos_pago MP
                   ON MP.id_metodo_pago = VP.id_metodo_pago
            LEFT JOIN usuarios U
                   ON U.id_usuarios = VP.id_usuarios
    WHERE   monto != 0)
UNION   ALL
SELECT  * FROM (
    SELECT  fecha_hora,
            monto,
            descripcion,
            MP.metodo,
            U.nombre
    FROM    caja C
            LEFT JOIN metodos_pago MP
                   ON MP.id_metodo_pago = C.id_metodo_pago
            LEFT JOIN usuarios U
                   ON U.id_usuarios = C.id_usuarios)
ORDER   BY 1 DESC;

CREATE VIEW VIEW_ALL_USUARIOS (USUARIO, NOMBRE, PERMISOS, ULTIMAVENTA)
AS SELECT  usuario,
        nombre,
        permisos,
        MAX(fecha_hora_creacion) AS ultimaVenta
FROM    Usuarios AS U
        LEFT JOIN Ventas AS V
               ON U.id_usuarios = V.id_usuarios
GROUP   BY 1, 2, 3
ORDER   BY UPPER(U.nombre) ASC;

CREATE VIEW VIEW_GRAN_FORMATO (CODIGO, DESCRIPCION, MIN_M2, PRECIO_M2)
AS SELECT  codigo,
        descripcion,
        min_m2,
        precio_m2
FROM    Productos_Gran_Formato AS P_gran
        LEFT JOIN Productos AS P
               ON P.id_productos = P_gran.id_productos
WHERE   P.is_active = 'true'
ORDER   BY P.id_productos;

CREATE VIEW VIEW_PRODUCTOS_SIMPLES (CODIGO, DESCRIPCION, PRECIO)
AS SELECT  codigo,
        descripcion
            || IIF(desde > 1, ', desde ' || ROUND(desde, 1) || ' unidades ', '')
            || IIF(duplex, '[PRECIO DUPLEX]', ''),
        precio_con_iva
FROM    Productos_Intervalos AS P_Inv
        LEFT JOIN Productos AS P
               ON P.id_productos = P_Inv.id_productos
WHERE   P.is_active = 'true'
ORDER   BY P.id_productos, desde, duplex ASC;


/******************** TRIGGERS ********************/

SET TERM ^ ;
CREATE TRIGGER DESCONTAR_INVENTARIO FOR VENTAS_DETALLADO ACTIVE
AFTER INSERT POSITION 0

AS
BEGIN
    MERGE   INTO INVENTARIO AS I
    USING   productos_utiliza_inventario AS PUI
            ON I.ID_INVENTARIO = PUI.ID_INVENTARIO
                AND PUI.ID_PRODUCTOS = new.ID_PRODUCTOS
    WHEN    MATCHED THEN
            UPDATE SET I.UNIDADES_RESTANTES = I.UNIDADES_RESTANTES
                                            - (CASE WHEN new.duplex
                                                   THEN CEIL(new.cantidad * PUI.UTILIZA_INVENTARIO / 2)
                                                   ELSE new.cantidad * PUI.UTILIZA_INVENTARIO
                                               END);
END
^
SET TERM ; ^
SET TERM ^ ;
CREATE TRIGGER EVENTO_PRODUCTOS FOR PRODUCTOS ACTIVE
AFTER INSERT OR DELETE OR UPDATE POSITION 0

AS
BEGIN
    POST_EVENT 'cambio_productos';
END
^
SET TERM ; ^


/********************
INSERT INTO CLIENTES (NOMBRE, TELEFONO, CORREO) VALUES ('Público general', 'N/A', 'N/A');

INSERT INTO USUARIOS (USUARIO, NOMBRE, PERMISOS) VALUES ('SYSDBA', 'Administrador DB', 'Administrador');

INSERT INTO METODOS_PAGO (METODO, COMISION_PORCENTAJE) VALUES ('Efectivo', '0.000000');
INSERT INTO METODOS_PAGO (METODO, COMISION_PORCENTAJE) VALUES ('Tarjeta de crédito', '0.000000');
INSERT INTO METODOS_PAGO (METODO, COMISION_PORCENTAJE) VALUES ('Tarjeta de débito', '0.000000');
INSERT INTO METODOS_PAGO (METODO, COMISION_PORCENTAJE) VALUES ('Transferencia bancaria', '0.000000');
********************/
