-- Migración: cliente libre (nombre/teléfono crudos) para ventas directas.
-- Ejecutar manualmente sobre bases de datos existentes en el despliegue.
ALTER TABLE VENTAS ADD NOMBRE_CLIENTE_DIRECTO VARCHAR(100);
ALTER TABLE VENTAS ADD TELEFONO_CLIENTE_DIRECTO VARCHAR(30);
