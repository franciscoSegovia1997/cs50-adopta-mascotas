# Datos de prueba. Uso: python seed.py
from werkzeug.security import generate_password_hash

from app import db

if not db.execute("SELECT id FROM users WHERE username = ?", "admin"):
    db.execute(
        "INSERT INTO users (username, email, hash) VALUES (?, ?, ?)",
        "admin", "admin@adoptaapp.com", generate_password_hash("admin123"),
    )
    print("Usuario creado -> admin / admin123")

for nombre, descripcion in [
    ("Perro", "Mascotas caninas de todas las razas"),
    ("Gato", "Mascotas felinas"),
]:
    if not db.execute("SELECT id FROM tipos_mascota WHERE nombre = ?", nombre):
        db.execute(
            "INSERT INTO tipos_mascota (nombre, descripcion) VALUES (?, ?)",
            nombre, descripcion,
        )

print("Seed completado.")
