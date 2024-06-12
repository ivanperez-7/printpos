/********************* ROLES **********************/

CREATE ROLE ADMINISTRADOR;
CREATE ROLE VENDEDOR;

/******************** TABLES **********************/

CREATE TABLE CAJA
(
  ID_MOVIMIENTO INTEGER GENERATED ALWAYS AS IDENTITY (START WITH 1) NOT NULL,
  FECHA_HORA TIMESTAMP NOT NULL,
  MONTO FLOAT NOT NULL,
  DESCRIPCION BLOB SUB_TYPE 1,
  ID_METODO_PAGO INTEGER NOT NULL,
  ID_USUARIOS INTEGER NOT NULL,
  CONSTRAINT PK_CAJA PRIMARY KEY (ID_MOVIMIENTO)
);
CREATE TABLE CLIENTES
(
  ID_CLIENTES INTEGER GENERATED ALWAYS AS IDENTITY (START WITH 1) NOT NULL,
  NOMBRE VARCHAR(100) NOT NULL,
  TELEFONO VARCHAR(30) NOT NULL,
  CORREO VARCHAR(100),
  DIRECCION VARCHAR(100),
  RFC VARCHAR(100),
  CLIENTE_ESPECIAL BOOLEAN DEFAULT false NOT NULL,
  DESCUENTOS BLOB SUB_TYPE 1,
  CONSTRAINT PK_CLIENTES PRIMARY KEY (ID_CLIENTES),
  CONSTRAINT UNIQUE_1 UNIQUE (NOMBRE,TELEFONO)
);
CREATE TABLE INVENTARIO
(
  ID_INVENTARIO INTEGER GENERATED ALWAYS AS IDENTITY (START WITH 1) NOT NULL,
  NOMBRE VARCHAR(50) NOT NULL,
  TAMANO_LOTE FLOAT NOT NULL,
  PRECIO_LOTE FLOAT NOT NULL,
  MINIMO_LOTES FLOAT NOT NULL,
  UNIDADES_RESTANTES FLOAT NOT NULL,
  CONSTRAINT PK_INVENTARIO PRIMARY KEY (ID_INVENTARIO),
  CONSTRAINT UNIQUE_2 UNIQUE (NOMBRE)
);
CREATE TABLE METODOS_PAGO
(
  ID_METODO_PAGO INTEGER GENERATED ALWAYS AS IDENTITY (START WITH 1) NOT NULL,
  METODO VARCHAR(30) NOT NULL,
  COMISION_PORCENTAJE FLOAT DEFAULT 0.0 NOT NULL,
  CONSTRAINT INTEG_62 PRIMARY KEY (ID_METODO_PAGO),
  CONSTRAINT INTEG_64 UNIQUE (METODO)
);
CREATE TABLE PRODUCTOS
(
  ID_PRODUCTOS INTEGER GENERATED ALWAYS AS IDENTITY (START WITH 1) NOT NULL,
  CODIGO VARCHAR(100) NOT NULL,
  DESCRIPCION VARCHAR(100) NOT NULL,
  ABREVIADO VARCHAR(50) NOT NULL,
  CATEGORIA VARCHAR(50) NOT NULL,
  CONSTRAINT PK_PRODUCTOS PRIMARY KEY (ID_PRODUCTOS),
  CONSTRAINT UNIQUE_3 UNIQUE (CODIGO)
);
CREATE TABLE PRODUCTOS_GRAN_FORMATO
(
  ID_PRODUCTOS INTEGER NOT NULL,
  MIN_M2 FLOAT NOT NULL,
  PRECIO_M2 FLOAT NOT NULL,
  CONSTRAINT UNIQUE_5 UNIQUE (ID_PRODUCTOS)
);
CREATE TABLE PRODUCTOS_INTERVALOS
(
  ID_PRODUCTOS INTEGER NOT NULL,
  DESDE FLOAT NOT NULL,
  PRECIO_CON_IVA FLOAT NOT NULL,
  DUPLEX BOOLEAN NOT NULL,
  CONSTRAINT UNIQUE_4 UNIQUE (ID_PRODUCTOS,DESDE,DUPLEX)
);
CREATE TABLE PRODUCTOS_UTILIZA_INVENTARIO
(
  ID_PRODUCTOS INTEGER NOT NULL,
  ID_INVENTARIO INTEGER NOT NULL,
  UTILIZA_INVENTARIO FLOAT NOT NULL,
  CONSTRAINT PK_PRODUCTOS_UTILIZA_INVENTARIO PRIMARY KEY (ID_PRODUCTOS,ID_INVENTARIO)
);
CREATE TABLE USUARIOS
(
  ID_USUARIOS INTEGER GENERATED ALWAYS AS IDENTITY (START WITH 1) NOT NULL,
  USUARIO VARCHAR(50) NOT NULL,
  NOMBRE VARCHAR(100) NOT NULL,
  PERMISOS VARCHAR(30),
  FOTO_PERFIL BLOB SUB_TYPE 0,
  CONSTRAINT PK_USUARIOS PRIMARY KEY (ID_USUARIOS),
  CONSTRAINT UNIQUE_6 UNIQUE (USUARIO)
);
CREATE TABLE VENTAS
(
  ID_VENTAS INTEGER GENERATED ALWAYS AS IDENTITY (START WITH 1) NOT NULL,
  ID_CLIENTES INTEGER NOT NULL,
  ID_USUARIOS INTEGER NOT NULL,
  FECHA_HORA_CREACION TIMESTAMP NOT NULL,
  FECHA_HORA_ENTREGA TIMESTAMP NOT NULL,
  COMENTARIOS BLOB SUB_TYPE 1,
  REQUIERE_FACTURA BOOLEAN NOT NULL,
  ESTADO BLOB SUB_TYPE 1 NOT NULL,
  CONSTRAINT PK_VENTAS PRIMARY KEY (ID_VENTAS)
);
CREATE TABLE VENTAS_DETALLADO
(
  ID_VENTAS INTEGER NOT NULL,
  ID_PRODUCTOS INTEGER NOT NULL,
  CANTIDAD FLOAT NOT NULL,
  PRECIO FLOAT NOT NULL,
  DESCUENTO FLOAT DEFAULT 0.0 NOT NULL,
  ESPECIFICACIONES BLOB SUB_TYPE 1 NOT NULL,
  DUPLEX BOOLEAN NOT NULL,
  IMPORTE FLOAT NOT NULL
);
CREATE TABLE VENTAS_PAGOS
(
  ID_PAGO INTEGER GENERATED BY DEFAULT AS IDENTITY (START WITH 1) NOT NULL,
  ID_VENTAS INTEGER NOT NULL,
  ID_METODO_PAGO INTEGER NOT NULL,
  FECHA_HORA TIMESTAMP NOT NULL,
  MONTO FLOAT NOT NULL,
  RECIBIDO FLOAT NOT NULL,
  CONSTRAINT INTEG_67 PRIMARY KEY (ID_PAGO)
);
/********************* VIEWS **********************/

CREATE VIEW MOVIMIENTOS_CAJA (FECHA_HORA, MONTO, DESCRIPCION, METODO, NOMBRE)
AS SELECT  * FROM (
    SELECT  fecha_hora,
            monto,
            CASE WHEN monto > 0 THEN 'Pago' ELSE 'Devoluci�n' END
                || ' de venta con folio ' || V.id_ventas AS descripcion,
            MP.metodo,
            U.nombre
    FROM    ventas_pagos VP
            LEFT JOIN ventas V
                   ON VP.id_ventas = V.id_ventas
            LEFT JOIN metodos_pago MP
                   ON MP.id_metodo_pago = VP.id_metodo_pago
            LEFT JOIN usuarios U
                   ON U.id_usuarios = V.id_usuarios
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

CREATE VIEW VIEW_GRAN_FORMATO (CODIGO, DESCRIPCION, MIN_M2, PRECIO_M2)
AS SELECT  codigo,
        descripcion, 
        min_m2,
        precio_m2
FROM    Productos_Gran_Formato AS P_gran
        LEFT JOIN Productos AS P
               ON P.id_productos = P_gran.id_productos
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
ORDER   BY P.id_productos, desde, duplex ASC;
/******************* EXCEPTIONS *******************/

/******************** TRIGGERS ********************/

SET TERM ^ ;
CREATE TRIGGER DESCONTAR_INVENTARIO FOR VENTAS_DETALLADO ACTIVE
AFTER INSERT POSITION 0

As
BEGIN
    MERGE INTO INVENTARIO AS I
        USING Productos_Utiliza_Inventario AS PUI
        ON I.ID_INVENTARIO = PUI.ID_INVENTARIO AND PUI.ID_PRODUCTOS = new.ID_PRODUCTOS
        WHEN MATCHED THEN
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
/******************** DB TRIGGERS ********************/


ALTER TABLE CAJA ADD CONSTRAINT FK_CAJA_METODO
  FOREIGN KEY (ID_METODO_PAGO) REFERENCES METODOS_PAGO (ID_METODO_PAGO);
ALTER TABLE CAJA ADD CONSTRAINT FK_CAJA_USUARIOS
  FOREIGN KEY (ID_USUARIOS) REFERENCES USUARIOS (ID_USUARIOS);
ALTER TABLE INVENTARIO ADD PRECIO_UNIDAD COMPUTED BY (PRECIO_LOTE / TAMANO_LOTE);
ALTER TABLE INVENTARIO ADD LOTES_RESTANTES COMPUTED BY (FLOOR(UNIDADES_RESTANTES / TAMANO_LOTE));
ALTER TABLE PRODUCTOS_GRAN_FORMATO ADD CONSTRAINT FK_PROD_GRANFORMATO
  FOREIGN KEY (ID_PRODUCTOS) REFERENCES PRODUCTOS (ID_PRODUCTOS);
ALTER TABLE VENTAS ADD CONSTRAINT FK_CLIENTES
  FOREIGN KEY (ID_CLIENTES) REFERENCES CLIENTES (ID_CLIENTES);
ALTER TABLE VENTAS ADD CONSTRAINT FK_VENTAS_USUARIOS
  FOREIGN KEY (ID_USUARIOS) REFERENCES USUARIOS (ID_USUARIOS);
ALTER TABLE VENTAS_DETALLADO ADD CONSTRAINT FK_VENTAS_DETALLADO_PRODUCTOS
  FOREIGN KEY (ID_PRODUCTOS) REFERENCES PRODUCTOS (ID_PRODUCTOS);
ALTER TABLE VENTAS_DETALLADO ADD CONSTRAINT FK_VENTAS_DETALLADO_VENTAS
  FOREIGN KEY (ID_VENTAS) REFERENCES VENTAS (ID_VENTAS);
ALTER TABLE VENTAS_PAGOS ADD CONSTRAINT FK_VENTAS_PAGOS1
  FOREIGN KEY (ID_VENTAS) REFERENCES VENTAS (ID_VENTAS);
ALTER TABLE VENTAS_PAGOS ADD CONSTRAINT FK_VENTAS_PAGOS2
  FOREIGN KEY (ID_METODO_PAGO) REFERENCES METODOS_PAGO (ID_METODO_PAGO);

GRANT INSERT, SELECT
 ON CAJA TO ROLE ADMINISTRADOR;

GRANT INSERT
 ON CAJA TO ROLE VENDEDOR;

GRANT DELETE, INSERT, SELECT, UPDATE
 ON CLIENTES TO ROLE ADMINISTRADOR;

GRANT INSERT, SELECT, UPDATE
 ON CLIENTES TO ROLE VENDEDOR;

GRANT DELETE, INSERT, SELECT, UPDATE
 ON INVENTARIO TO ROLE ADMINISTRADOR;

GRANT SELECT, UPDATE
 ON INVENTARIO TO ROLE VENDEDOR;

GRANT SELECT
 ON METODOS_PAGO TO ROLE ADMINISTRADOR;

GRANT SELECT
 ON METODOS_PAGO TO ROLE VENDEDOR;

GRANT DELETE, INSERT, SELECT, UPDATE
 ON PRODUCTOS TO ROLE ADMINISTRADOR;

GRANT SELECT
 ON PRODUCTOS TO ROLE VENDEDOR;

GRANT DELETE, INSERT, SELECT, UPDATE
 ON PRODUCTOS_GRAN_FORMATO TO ROLE ADMINISTRADOR;

GRANT SELECT
 ON PRODUCTOS_GRAN_FORMATO TO ROLE VENDEDOR;

GRANT DELETE, INSERT, SELECT, UPDATE
 ON PRODUCTOS_INTERVALOS TO ROLE ADMINISTRADOR;

GRANT SELECT
 ON PRODUCTOS_INTERVALOS TO ROLE VENDEDOR;

GRANT DELETE, INSERT, SELECT, UPDATE
 ON PRODUCTOS_UTILIZA_INVENTARIO TO ROLE ADMINISTRADOR;

GRANT SELECT
 ON PRODUCTOS_UTILIZA_INVENTARIO TO ROLE VENDEDOR;

GRANT INSERT, SELECT, UPDATE
 ON USUARIOS TO ROLE ADMINISTRADOR;

GRANT SELECT
 ON USUARIOS TO ROLE VENDEDOR;

GRANT INSERT, SELECT, UPDATE
 ON VENTAS TO ROLE ADMINISTRADOR;

GRANT INSERT, SELECT, UPDATE
 ON VENTAS TO ROLE VENDEDOR;

GRANT INSERT, SELECT
 ON VENTAS_DETALLADO TO ROLE ADMINISTRADOR;

GRANT INSERT, SELECT
 ON VENTAS_DETALLADO TO ROLE VENDEDOR;

GRANT INSERT, SELECT
 ON VENTAS_PAGOS TO ROLE ADMINISTRADOR;

GRANT INSERT, SELECT
 ON VENTAS_PAGOS TO ROLE VENDEDOR;

GRANT SELECT
 ON MOVIMIENTOS_CAJA TO ROLE ADMINISTRADOR;

GRANT SELECT
 ON VIEW_GRAN_FORMATO TO ROLE ADMINISTRADOR;

GRANT SELECT
 ON VIEW_GRAN_FORMATO TO ROLE VENDEDOR;

GRANT SELECT
 ON VIEW_PRODUCTOS_SIMPLES TO ROLE ADMINISTRADOR;

GRANT SELECT
 ON VIEW_PRODUCTOS_SIMPLES TO ROLE VENDEDOR;

GRANT ADMINISTRADOR TO SYSDBA WITH ADMIN OPTION;
GRANT VENDEDOR TO SYSDBA WITH ADMIN OPTION;

/******************** 
INSERT INTO CLIENTES (NOMBRE, TELEFONO, CORREO) VALUES ('Público general', 'N/A', 'N/A');

INSERT INTO USUARIOS (USUARIO, NOMBRE, PERMISOS) VALUES ('SYSDBA', 'Administrador DB', 'Administrador');

INSERT INTO METODOS_PAGO (METODO, COMISION_PORCENTAJE) VALUES ('Efectivo', '0.000000');
INSERT INTO METODOS_PAGO (METODO, COMISION_PORCENTAJE) VALUES ('Tarjeta de crédito', '0.000000');
INSERT INTO METODOS_PAGO (METODO, COMISION_PORCENTAJE) VALUES ('Tarjeta de débito', '0.000000');
INSERT INTO METODOS_PAGO (METODO, COMISION_PORCENTAJE) VALUES ('Transferencia bancaria', '0.000000');
********************/
