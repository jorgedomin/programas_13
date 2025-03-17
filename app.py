from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
from database.conexion import init_db, db
from database.models import Usuario
import json
import csv

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Iniciar conexión a la BD con SQLAlchemy
init_db(app)

# Definición del formulario de contacto
class ContactForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired()])
    email = EmailField("Correo Electrónico", validators=[DataRequired(), Email()])
    mensaje = TextAreaField("Mensaje", validators=[DataRequired()])
    submit = SubmitField("Enviar")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/productos")
def productos():
    return render_template("productos.html")

@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    form = ContactForm()
    if form.validate_on_submit():
        # Guardar en MySQL
        nuevo_usuario = Usuario(
            nombre=form.nombre.data,
            email=form.email.data,
            mensaje=form.mensaje.data  # Se guarda también el mensaje en MySQL
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash(f"Mensaje enviado por {form.nombre.data} ({form.email.data})", "success")

        # Guardar en TXT
        with open("datos/datos.txt", "a") as file:
            file.write(f"{form.nombre.data}, {form.email.data}, {form.mensaje.data}\n")

        # Guardar en JSON
        datos = {"nombre": form.nombre.data, "email": form.email.data, "mensaje": form.mensaje.data}
        with open("datos/datos.json", "a") as file:
            json.dump(datos, file)
            file.write("\n")

        # Guardar en CSV
        with open("datos/datos.csv", "a", newline='') as file:
            writer = csv.writer(file)
            writer.writerow([form.nombre.data, form.email.data, form.mensaje.data])

        return redirect(url_for("index"))
    return render_template("contacto.html", form=form)

@app.route("/usuarios")
def obtener_usuarios():
    usuarios = Usuario.query.all()
    return render_template("usuario.html", usuarios=usuarios)

@app.route("/agregar_usuario", methods=["POST"])
def agregar_usuario():
    nombre = request.form["nombre"]
    email = request.form["email"]
    nuevo_usuario = Usuario(nombre=nombre, email=email)
    db.session.add(nuevo_usuario)
    db.session.commit()
    return redirect(url_for("obtener_usuarios"))

@app.route("/eliminar_usuario/<int:id>")
def eliminar_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
    return redirect(url_for("obtener_usuarios"))

@app.route("/leer_txt")
def leer_txt():
    with open("datos/datos.txt", "r") as file:
        contenido = file.readlines()
    return jsonify(contenido)

@app.route("/leer_json")
def leer_json():
    with open("datos/datos.json", "r") as file:
        contenido = [json.loads(line) for line in file]
    return jsonify(contenido)

@app.route("/leer_csv")
def leer_csv():
    with open("datos/datos.csv", "r") as file:
        reader = csv.reader(file)
        contenido = [row for row in reader]
    return jsonify(contenido)

if __name__ == "__main__":
    app.run(debug=True)
