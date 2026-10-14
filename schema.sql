-- Esquema de la base de datos (se ejecuta la primera vez que corres app.py)

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT,
    hash TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users (username);

CREATE TABLE IF NOT EXISTS tipos_mascota (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS mascotas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    edad INTEGER NOT NULL,
    descripcion TEXT,
    foto TEXT NOT NULL,
    estado TEXT DEFAULT 'Disponible',
    tipo_id INTEGER NOT NULL,
    FOREIGN KEY (tipo_id) REFERENCES tipos_mascota (id)
);

CREATE TABLE IF NOT EXISTS personas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    email TEXT,
    telefono TEXT
);

CREATE TABLE IF NOT EXISTS adopciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mascota_id INTEGER NOT NULL UNIQUE,
    persona_id INTEGER NOT NULL,
    fecha_adopcion TEXT,
    FOREIGN KEY (mascota_id) REFERENCES mascotas (id),
    FOREIGN KEY (persona_id) REFERENCES personas (id)
);
