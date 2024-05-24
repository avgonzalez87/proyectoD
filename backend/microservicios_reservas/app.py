from flask import Flask, request, jsonify
from datetime import datetime
import psycopg2
import psycopg2.extras

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

def serialize_reserva(reserva):
    return {
        'id': reserva['id'],
        'fecha': reserva['fecha'].isoformat() if reserva['fecha'] else None,
        'hora': reserva['hora'].strftime('%H:%M:%S') if reserva['hora'] else None,
        'estado': reserva['estado'],
        'detalle': reserva['detalle']
    }

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

@app.route('/reservas', methods=['POST'])
def crear_reserva():
    data = request.get_json()
    if not data:
        return ResponseFactory.create_response('error', 'No se recibieron datos')

    required_fields = ['fecha', 'hora', 'estado', 'detalle']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return ResponseFactory.create_response('error', f"Faltan campos obligatorios: {', '.join(missing_fields)}")

    try:
        fecha = datetime.strptime(data['fecha'], "%Y-%m-%d").date()
        hora = datetime.strptime(data['hora'], "%H:%M").time()
    except ValueError as e:
        return ResponseFactory.create_response('error', f"Formato de fecha o hora incorrecto: {str(e)}")

    usuario_responsable = data['usuario_responsable']

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT numero_mesa FROM mesas WHERE disponible = TRUE LIMIT 1;")
        mesa = cursor.fetchone()
        if not mesa:
            return ResponseFactory.create_response('error', 'No hay mesas disponibles')

        numero_mesa = mesa['numero_mesa']
        
        cursor.execute(
            "INSERT INTO reservas (fecha, hora, estado, detalle, usuario_responsable, numero_mesa) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, fecha, hora, estado, detalle;",
            (fecha, hora, data['estado'], data['detalle'], usuario_responsable, numero_mesa)
        )
        reserva = cursor.fetchone()
        if not reserva:
            return ResponseFactory.create_response('error', 'Error al crear la reserva')

        cursor.execute(
            "UPDATE mesas SET disponible = FALSE, usuario_responsable = %s WHERE numero_mesa = %s;",
            (usuario_responsable, numero_mesa)
        )

        reserva_serializada = serialize_reserva(reserva)
        conn.commit()
        return ResponseFactory.create_response('success', 'Reserva creada con éxito', reserva_serializada)
    except psycopg2.DatabaseError as e:
        conn.rollback()
        return ResponseFactory.create_response('error', str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/delete_reserva/<int:reserva_id>', methods=['DELETE'])
def delete_reserva(reserva_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT numero_mesa FROM reservas WHERE id = %s", (reserva_id,))
        reserva = cursor.fetchone()
        if reserva:
            cursor.execute("DELETE FROM reservas WHERE id = %s RETURNING id;", (reserva_id,))
            deleted_id = cursor.fetchone()
            if deleted_id:
                cursor.execute(
                    "UPDATE mesas SET disponible = True WHERE numero_mesa = %s;",
                    (reserva['numero_mesa'],)
                )
            conn.commit()
            return ResponseFactory.create_response('success', 'Reserva eliminada con éxito')
        else:
            return ResponseFactory.create_response('not_found', 'Reserva no encontrada')
    except psycopg2.DatabaseError as e:
        conn.rollback()
        return ResponseFactory.create_response('error', str(e))
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=3100)
