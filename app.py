import os
import sqlite3
from datetime import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import apology, login_required
from forms import TipoMascotaForm

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-insecure-cambia-esto")

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
EXTENSIONES_OK = {"png", "jpg", "jpeg", "gif", "webp"}

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Crea la base de datos la primera vez a partir de schema.sql
DB_PATH = os.path.join(app.root_path, "adoptaapp.db")
if not os.path.exists(DB_PATH):
    with sqlite3.connect(DB_PATH) as _con:
        with open(os.path.join(app.root_path, "schema.sql")) as _f:
            _con.executescript(_f.read())

db = SQL("sqlite:///" + DB_PATH)


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = "0"
    response.headers["Pragma"] = "no-cache"
    return response


def guardar_foto(archivo):
    if not archivo or not archivo.filename:
        return None

    nombre = secure_filename(archivo.filename)
    ext = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else ""
    if ext not in EXTENSIONES_OK:
        return None

    base = nombre.rsplit(".", 1)[0]
    destino, i = nombre, 1
    while os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], destino)):
        destino = f"{base}_{i}.{ext}"
        i += 1

    archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], destino))
    return destino


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("falta el usuario", 400)
        if not password:
            return apology("falta la contrasena", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("usuario o contrasena invalidos", 403)

        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        return redirect("/")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("falta el usuario", 400)
        if not password:
            return apology("falta la contrasena", 400)
        if password != confirmation:
            return apology("las contrasenas no coinciden", 400)

        if db.execute("SELECT id FROM users WHERE username = ?", username):
            return apology("ese usuario ya existe", 400)

        db.execute(
            "INSERT INTO users (username, email, hash) VALUES (?, ?, ?)",
            username, email, generate_password_hash(password),
        )
        flash("Cuenta creada. Ya puedes iniciar sesion.")
        return redirect("/login")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/")
@login_required
def home():
    tipos = db.execute("SELECT * FROM tipos_mascota ORDER BY nombre")
    mascotas = db.execute("SELECT * FROM mascotas ORDER BY id DESC")
    return render_template("home.html", tipos=tipos, mascotas=mascotas)


@app.route("/crearTipo", methods=["GET", "POST"])
@login_required
def crear_tipo():
    form = TipoMascotaForm()

    if form.validate_on_submit():
        nombre = form.nombre.data.strip()
        descripcion = (form.descripcion.data or "").strip()

        if db.execute("SELECT id FROM tipos_mascota WHERE LOWER(nombre) = LOWER(?)", nombre):
            form.nombre.errors.append("Este tipo de mascota ya existe")
        else:
            db.execute(
                "INSERT INTO tipos_mascota (nombre, descripcion) VALUES (?, ?)",
                nombre, descripcion,
            )
            return redirect(url_for("home"))

    tipos = db.execute("SELECT * FROM tipos_mascota ORDER BY nombre")
    return render_template("crearTipo.html", form=form, tipos=tipos)


@app.route("/crearMascota", methods=["GET", "POST"])
@login_required
def crear_mascota():
    tipos = db.execute("SELECT * FROM tipos_mascota ORDER BY nombre")

    if request.method == "POST":
        nombre = request.form.get("nombre")
        edad = request.form.get("edad")
        descripcion = request.form.get("descripcion")
        tipo_id = request.form.get("tipo")
        foto = request.files.get("foto")

        if not nombre or not edad or not tipo_id:
            return apology("faltan datos de la mascota", 400)
        try:
            edad = int(edad)
        except (TypeError, ValueError):
            return apology("la edad debe ser un numero", 400)

        nombre_foto = guardar_foto(foto)
        if not nombre_foto:
            return apology("sube una imagen valida (png, jpg, jpeg, gif, webp)", 400)

        db.execute(
            "INSERT INTO mascotas (nombre, edad, descripcion, foto, estado, tipo_id) "
            "VALUES (?, ?, ?, ?, 'Disponible', ?)",
            nombre, edad, descripcion, nombre_foto, tipo_id,
        )
        return redirect(url_for("home"))

    return render_template("crearMascota.html", tipos=tipos)


@app.route("/detalleMascota/<int:id_mascota>", methods=["GET", "POST"])
@login_required
def detalle_mascota(id_mascota):
    filas = db.execute(
        "SELECT mascotas.*, tipos_mascota.nombre AS tipo_nombre "
        "FROM mascotas JOIN tipos_mascota ON mascotas.tipo_id = tipos_mascota.id "
        "WHERE mascotas.id = ?",
        id_mascota,
    )
    if not filas:
        return apology("mascota no encontrada", 404)
    mascota = filas[0]

    if request.method == "POST":
        if mascota["estado"] != "Disponible":
            return apology("esta mascota ya fue adoptada", 400)

        nombre = request.form.get("nombre")
        email = request.form.get("email")
        telefono = request.form.get("telefono")
        if not nombre or not email or not telefono:
            return apology("faltan datos del adoptante", 400)

        persona_id = db.execute(
            "INSERT INTO personas (nombre, email, telefono) VALUES (?, ?, ?)",
            nombre, email, telefono,
        )
        db.execute(
            "INSERT INTO adopciones (mascota_id, persona_id, fecha_adopcion) "
            "VALUES (?, ?, ?)",
            id_mascota, persona_id, datetime.now().strftime("%d/%m/%Y %H:%M"),
        )
        db.execute("UPDATE mascotas SET estado = 'Adoptado' WHERE id = ?", id_mascota)
        return redirect(url_for("detalle_mascota", id_mascota=id_mascota))

    adopcion = None
    if mascota["estado"] == "Adoptado":
        filas = db.execute(
            "SELECT adopciones.fecha_adopcion, "
            "personas.nombre AS persona_nombre, "
            "personas.email AS persona_email, "
            "personas.telefono AS persona_telefono "
            "FROM adopciones JOIN personas ON adopciones.persona_id = personas.id "
            "WHERE adopciones.mascota_id = ?",
            id_mascota,
        )
        adopcion = filas[0] if filas else None

    tipos = db.execute("SELECT * FROM tipos_mascota ORDER BY nombre")
    return render_template(
        "detalleMascota.html", mascota=mascota, tipos=tipos, adopcion=adopcion
    )


@app.route("/mascotasxtipo/<int:id_tipo>")
@login_required
def mascotas_por_tipo(id_tipo):
    tipos = db.execute("SELECT * FROM tipos_mascota ORDER BY nombre")

    filas = db.execute("SELECT * FROM tipos_mascota WHERE id = ?", id_tipo)
    if not filas:
        return apology("tipo no encontrado", 404)
    tipo = filas[0]

    mascotas = db.execute(
        "SELECT * FROM mascotas WHERE tipo_id = ? ORDER BY id DESC", id_tipo
    )
    return render_template(
        "home.html", tipos=tipos, mascotas=mascotas, tipo_seleccionado=tipo
    )


@app.route("/listaAdoptantes")
@login_required
def lista_adoptantes():
    tipos = db.execute("SELECT * FROM tipos_mascota ORDER BY nombre")
    adopciones = db.execute(
        "SELECT adopciones.fecha_adopcion, "
        "mascotas.nombre AS mascota_nombre, "
        "personas.nombre AS persona_nombre, "
        "personas.email AS persona_email, "
        "personas.telefono AS persona_telefono "
        "FROM adopciones "
        "JOIN mascotas ON adopciones.mascota_id = mascotas.id "
        "JOIN personas ON adopciones.persona_id = personas.id "
        "ORDER BY adopciones.id DESC"
    )
    return render_template(
        "listaAdoptantes.html", tipos=tipos, adopciones=adopciones
    )


if __name__ == "__main__":
    app.run(debug=True)
