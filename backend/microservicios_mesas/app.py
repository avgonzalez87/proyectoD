from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

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

@app.route('/login', methods=['POST'])
def login():
    correo = request.json.get('correo', None)
    contrasena = request.json.get('contrasena', None)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, tipo_usuario FROM usuarios WHERE correo = %s AND contrasena = %s", (correo, contrasena))
    user_info = cursor.fetchone()
    cursor.close()
    conn.close()

    if user_info:
        return ResponseFactory.create_response('success', 'Login exitoso', {'user_id': user_info[0], 'tipo_usuario': user_info[1]})
    else:
        return ResponseFactory.create_response('error', 'Credenciales inválidas')

@app.route('/mesas', methods=['POST'])
def crear_mesa():
    data = request.get_json()
    numero_mesa = data['numero_mesa']
    personas = data['personas']
    localizacion = data['localizacion']
    usuario_responsable = data['usuario_responsable']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO mesas (numero_mesa, personas, localizacion, disponible, usuario_responsable, reserva_id) VALUES (%s, %s, %s, True, %s, NULL) RETURNING numero_mesa;',
            (numero_mesa, personas, localizacion, usuario_responsable)
        )
        numero_mesa = cursor.fetchone()[0]
        conn.commit()
        return ResponseFactory.create_response('success', 'Mesa creada con éxito', {"numero_mesa": numero_mesa})
    except psycopg2.DatabaseError as e:
        conn.rollback()
        return ResponseFactory.create_response('error', str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/mesas/<int:numero_mesa>', methods=['PUT'])
def actualizar_mesa(numero_mesa):
    data = request.get_json()
    personas = data.get('personas')
    localizacion = data.get('localizacion')
    disponible = data.get('disponible', True)
    usuario_responsable = data['usuario_responsable']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT reserva_id FROM mesas WHERE numero_mesa = %s", (numero_mesa,))
        mesa_info = cursor.fetchone()
        if mesa_info and mesa_info['reserva_id'] is not None and disponible:
            return ResponseFactory.create_response('error', "No se puede marcar como disponible una mesa reservada")

        cursor.execute(
            "UPDATE mesas SET personas = %s, localizacion = %s, disponible = %s, usuario_responsable = %s WHERE numero_mesa = %s RETURNING numero_mesa;",
            (personas, localizacion, disponible, usuario_responsable, numero_mesa)
        )
        updated_mesa = cursor.fetchone()
        if not updated_mesa:
            return ResponseFactory.create_response('not_found', "Mesa no encontrada")
        conn.commit()
        return ResponseFactory.create_response('success', "Mesa actualizada con éxito", {"numero_mesa": updated_mesa[0]})
    except psycopg2.DatabaseError as e:
        conn.rollback()
        return ResponseFactory.create_response('error', str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/mesas/<int:numero_mesa>', methods=['GET'])
def get_mesa(numero_mesa):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT numero_mesa, personas, localizacion, disponible, usuario_responsable FROM mesas WHERE numero_mesa = %s", (numero_mesa,))
        mesa = cursor.fetchone()
        if mesa:
            mesa_info = {
                'numero_mesa': mesa[0],
                'personas': mesa[1],
                'localizacion': mesa[2],
                'disponible': mesa[3],
                'usuario_responsable': mesa[4]
            }
            return ResponseFactory.create_response('success', 'Mesa encontrada', mesa_info)
        else:
            return ResponseFactory.create_response('not_found', 'Mesa no encontrada')
    except psycopg2.DatabaseError as e:
        return ResponseFactory.create_response('error', str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/mesas/<int:numero_mesa>', methods=['DELETE'])
def delete_mesa(numero_mesa):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM mesas WHERE numero_mesa = %s RETURNING numero_mesa;", (numero_mesa,))
        deleted_mesa = cursor.fetchone()
        if not deleted_mesa:
            return ResponseFactory.create_response('not_found', "Mesa no encontrada")
        conn.commit()
        return ResponseFactory.create_response('success', "Mesa eliminada con éxito")
    except psycopg2.DatabaseError as e:
        return ResponseFactory.create_response('error', str(e))
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=3300)
