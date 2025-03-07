from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
import json
import os
import bcrypt
import logging

# Configurar el logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_LOGGER = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configurar la carpeta de archivos estáticos
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static')

# Cargar usuarios
usuarios_path = os.path.join(os.path.dirname(__file__), 'static/usuarios.json')
if os.path.exists(usuarios_path):
    with open(usuarios_path, 'r', encoding='utf-8') as f:
        try:
            usuarios = json.load(f)
        except json.JSONDecodeError as e:
            _LOGGER.error("Error decoding JSON: %s", e)
            usuarios = []
else:
    _LOGGER.warning("Usuarios no encontrados")
    usuarios = []

# Cargar partidos
partidos_path = os.path.join(os.path.dirname(__file__), 'static/partidos.json')
if os.path.exists(partidos_path):
    with open(partidos_path, 'r', encoding='utf-8') as f:
        partidos = json.load(f)
else:
    _LOGGER.warning("Partidos no encontrados")
    partidos = []

# Cargar inscripciones
inscripciones_path = os.path.join(os.path.dirname(__file__), 'static/inscripciones.json')
if os.path.exists(inscripciones_path):
    with open(inscripciones_path, 'r', encoding='utf-8') as f:
        inscripciones = json.load(f)
else:
    _LOGGER.warning("Inscripciones no encontrados")
    inscripciones = []

_LOGGER.info("Carga completada")

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para el login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        
        for usuario in usuarios:
            _LOGGER.info("usuario: %s", usuario)
            if usuario['username'] == username:
                _LOGGER.info("password: %s y %s", password, usuario['password'].encode('utf-8'))
                if bcrypt.checkpw(password, usuario['password'].encode('utf-8')):
                    session['username'] = username
                    session['admin'] = usuario['admin']
                    return redirect(url_for('index'))
        
        return 'Usuario o contraseña incorrectos.'
    
    return render_template('login.html')

# Ruta para registrar un nuevo usuario (solo administradores)
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if not session.get('admin'):
        return 'Acceso denegado.', 403

    if request.method == 'POST':
        username = request.form['username']
        nombre_completo = request.form['nombre_completo']
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        admin = request.form.get('admin') == 'on'
        _LOGGER.info("usuarios: %s", usuarios)
        # Comprobar si el username ya existe
        for usuario in usuarios:
            if usuario['username'] == username:
                return 'El nombre de usuario ya existe.'

        nuevo_usuario = {
            'username': username,
            'nombre_completo': nombre_completo,
            'password': password.decode('utf-8'),
            'admin': admin
        }
        
        usuarios.append(nuevo_usuario)
        with open(usuarios_path, 'w', encoding='utf-8') as f:
            json.dump(usuarios, f, indent=4)

        return redirect(url_for('index'))
    
    return render_template('registro.html')

# Ruta para crear un nuevo partido
@app.route('/nuevo_partido', methods=['GET', 'POST'])
def nuevo_partido():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        fecha_hora = request.form['fecha_hora']
        partido = {
            'fecha_hora': fecha_hora,
            'jugadores': [
                {'nombre': session['username'], 'posicion': 'Creador', 'lado': 'N/A'}
            ]
        }
        
        partidos.append(partido)
        with open(partidos_path, 'w', encoding='utf-8') as f:
            json.dump(partidos, f, indent=4)

        return redirect(url_for('inscribirse'))
    return render_template('nuevo_partido.html')

# Ruta para inscribirse en un partido
@app.route('/inscribirse', methods=['GET', 'POST'])
def inscribirse():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        partido_index = int(request.form['partido_index'])
        nombre = session['username']
        posicion = request.form['posicion']
        lado = request.form['lado']

        # Verificar si el partido ya tiene 4 jugadores
        inscripciones_partido = [i for i in inscripciones if i['partido_index'] == partido_index]
        if len(inscripciones_partido) >= 4:
            return 'Este partido ya está completo.'

        inscripcion = {
            'partido_index': partido_index,
            'nombre': nombre,
            'posicion': posicion,
            'lado': lado
        }
        inscripciones.append(inscripcion)

        with open(inscripciones_path, 'w', encoding='utf-8') as f:
            json.dump(inscripciones, f, indent=4)

        return redirect(url_for('index'))

    return render_template('inscribirse.html', partidos=partidos, inscripciones=inscripciones)

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('admin', None)
    return redirect(url_for('index'))

# Ruta para servir archivos estáticos
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)