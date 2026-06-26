PRAGMA foreign_keys = ON;


BEGIN TRANSACTION;


-- ----------------------------------------
-- TABLA UNIDAD
-- ----------------------------------------


CREATE TABLE IF NOT EXISTS unidad (


    id_unidad INTEGER PRIMARY KEY AUTOINCREMENT,
    placa TEXT NOT NULL UNIQUE


);


-- ----------------------------------------
-- TABLA OPERADOR
-- ----------------------------------------


CREATE TABLE IF NOT EXISTS operador (


    id_operador INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    telefono TEXT NOT NULL,
    id_unidad INTEGER,


    FOREIGN KEY (id_unidad)
    REFERENCES unidad(id_unidad)
    ON DELETE CASCADE
    ON UPDATE RESTRICT


);


-- ----------------------------------------
-- TABLA RUTA
-- ----------------------------------------


CREATE TABLE IF NOT EXISTS ruta (


    id_ruta INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    direccion TEXT NOT NULL


);


-- ----------------------------------------
-- TABLA HORARIO
-- ----------------------------------------


CREATE TABLE IF NOT EXISTS horario (


    id_horario INTEGER PRIMARY KEY AUTOINCREMENT,
    hora_inicio TEXT NOT NULL,
    hora_termino TEXT NOT NULL,
    id_ruta INTEGER,
    id_unidad INTEGER,


    FOREIGN KEY (id_ruta)
    REFERENCES ruta(id_ruta)
    ON DELETE CASCADE
    ON UPDATE RESTRICT,


    FOREIGN KEY (id_unidad)
    REFERENCES unidad(id_unidad)
    ON DELETE CASCADE
    ON UPDATE RESTRICT


);


CREATE TABLE usuario (


    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,


    nombre TEXT NOT NULL UNIQUE,


    contrasena TEXT NOT NULL,


    rol TEXT NOT NULL


);


-- ----------------------------------------
-- ÍNDICES
-- ----------------------------------------


CREATE INDEX IF NOT EXISTS idx_operador_id_unidad
ON operador(id_unidad);


CREATE INDEX IF NOT EXISTS idx_horario_id_ruta
ON horario(id_ruta);


CREATE INDEX IF NOT EXISTS idx_horario_id_unidad
ON horario(id_unidad);


COMMIT;



