from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = 'tu_super_secreto'
CORS(app)  # Habilitar CORS para todas las rutas

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = psycopg2.connect(
                dbname="Restaurante",
                user="postgres",
                password="adm",
                host="localhost"
            )
        return cls._instance

    def get_connection(self):
        return self.connection

def get_db_connection():
    return DatabaseConnection().get_connection()

class ResponseFactory:
    @staticmethod
    def create_response(response_type, message, data=None):
        if response_type == 'success':
            return jsonify({'status': 'success', 'message': message, 'data': data}), 200
        elif response_type == 'error':
            return jsonify({'status': 'error', 'message': message}), 400
        elif response_type == 'not_found':
            return jsonify({'status': 'not_found', 'message': message}), 404

@app.route('/')
def home():
    return 'Bienvenido a la API de ReservaFacil!'

@app.route('/create_user', methods=['POST'])
def create_user():
    user_details = request.json
    nombre = user_details['nombre']
    apellido = user_details['apellido']
    correo = user_details['correo']
    telefono = user_details['telefono']
    tipo_usuario = user_details['tipo_usuario']
    contrasena = user_details['contrasena']

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO public.usuarios (nombre, apellido, correo, telefono, tipo_usuario, contrasena) VALUES (%s, %s, %s, %s, %s, %s)',
            (nombre, apellido, correo, telefono, tipo_usuario, contrasena)
        )
        conn.commit()
        return ResponseFactory.create_response('success', 'Usuario creado exitosamente')
    except psycopg2.DatabaseError as e:
        return ResponseFactory.create_response('error', str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/login', methods=['POST'])
def login():
    credentials = request.json
    correo = credentials['correo']
    contrasena = credentials['contrasena']

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(
            'SELECT * FROM public.usuarios WHERE correo = %s AND contrasena = %s',
            (correo, contrasena)
        )
        user = cursor.fetchone()
        if user:
            additional_claims = {"tipo_usuario": user['tipo_usuario']}
            return ResponseFactory.create_response('success', 'Login exitoso', {'user': user['correo'], 'tipo_usuario': additional_claims})
        else:
            return ResponseFactory.create_response('error', 'Credenciales inválidas')
    except psycopg2.DatabaseError as e:
        return ResponseFactory.create_response('error', str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM public.usuarios WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return ResponseFactory.create_response('not_found', 'Usuario no encontrado')
        return ResponseFactory.create_response('success', 'Usuario encontrado', user)
    except psycopg2.DatabaseError as e:
        return ResponseFactory.create_response('error', str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user_details = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE public.usuarios SET nombre=%s, apellido=%s, correo=%s, telefono=%s, tipo_usuario=%s, contrasena=%s WHERE id=%s RETURNING id",
            (user_details['nombre'], user_details['apellido'], user_details['correo'], user_details['telefono'], user_details['tipo_usuario'], user_details['contrasena'], user_id)
        )
        updated_user = cursor.fetchone()
        if updated_user is None:
            return ResponseFactory.create_response('not_found', 'Usuario no encontrado')
        conn.commit()
        return ResponseFactory.create_response('success', 'Usuario actualizado exitosamente')
    except psycopg2.DatabaseError as e:
        return ResponseFactory.create_response('error', str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM public.usuarios WHERE id = %s RETURNING id", (user_id,))
        deleted_user = cursor.fetchone()
        if deleted_user is None:
            return ResponseFactory.create_response('not_found', 'Usuario no encontrado')
        conn.commit()
        return ResponseFactory.create_response('success', 'Usuario eliminado exitosamente')
    except psycopg2.DatabaseError as e:
        return ResponseFactory.create_response('error', str(e))
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=3200)
