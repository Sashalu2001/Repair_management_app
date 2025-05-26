from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from decimal import Decimal

app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5000", "http://localhost"]}})

# Подключение к базе данных
db = mysql.connector.connect(
    host="localhost",
    user="Sashalu",
    password="sashalu",
    database="repair_management"
)
cursor = db.cursor(dictionary=True)


def convert_decimal(data):
    if isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, dict):
        return {k: convert_decimal(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimal(item) for item in data]
    return data


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

'''
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    cursor.execute("SELECT * FROM users WHERE login = %s AND password = %s",
                   (data['login'], data['password']))
    user = cursor.fetchone()
    if user:
        return jsonify({'status': 'success', 'user': convert_decimal(user)})
    return jsonify({'status': 'error', 'message': 'Неверные данные'}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    cursor.execute("SELECT * FROM users WHERE login = %s", (data['login'],))
    if cursor.fetchone():
        return jsonify({'status': 'error', 'message': 'Логин занят'}), 400
    cursor.execute("INSERT INTO users (login, password, contact, role) VALUES (%s, %s, %s, 'user')",
                   (data['login'], data['password'], data['contact']))
    db.commit()
    return jsonify({'status': 'success'})
'''

@app.route('/load_data', methods=['GET'])
def load_data():
    try:
        cursor.execute("SELECT name FROM contractors")
        contractors = [row['name'] for row in cursor.fetchall()]

        cursor.execute("SELECT name, price FROM materials")
        materials = {row['name']: float(row['price']) for row in cursor.fetchall()}

        cursor.execute("SELECT name FROM objects")
        objects = [row['name'] for row in cursor.fetchall()]

        cursor.execute("SELECT name, multiplier FROM types_of_work")
        types_of_work = {row['name']: float(row['multiplier']) for row in cursor.fetchall()}

        cursor.execute("SELECT status FROM order_statuses")
        order_statuses = [row['status'] for row in cursor.fetchall()]

        return jsonify({
            'status': 'success',
            'contractors': contractors,
            'materials': materials,
            'objects': objects,
            'types_of_work': types_of_work,
            'order_statuses': order_statuses
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/create_order', methods=['POST'])
def create_order():
    try:
        data = request.json

        # Преобразование входных данных
        contractor = data.get('contractor')
        materials = {k: float(v) for k, v in data.get('materials', {}).items()}  # Преобразуем цены материалов в float
        obj = data.get('object')
        work_type = data.get('work_type')
        customer_price = float(data.get('customer_price'))  # Преобразуем в float
        area = float(data.get('area'))  # Преобразуем в float
        user_id = int(data.get('user_id'))  # Преобразуем в int

        # Получение ID подрядчика, объекта и типа работы
        cursor.execute("SELECT id FROM contractors WHERE name = %s", (contractor,))
        contractor_id = cursor.fetchone()['id']

        cursor.execute("SELECT id FROM objects WHERE name = %s", (obj,))
        object_id = cursor.fetchone()['id']

        cursor.execute("SELECT id, multiplier FROM types_of_work WHERE name = %s", (work_type,))
        type_of_work = cursor.fetchone()
        type_of_work_id = type_of_work['id']
        multiplier = float(type_of_work['multiplier'])  # Преобразуем множитель в float

        # Расчет стоимости
        material_cost = sum(materials.values())  # Сумма цен материалов
        cost = material_cost + (multiplier * customer_price * area)  # Общая стоимость

        # Сохранение заказа в базу данных
        cursor.execute("""
            INSERT INTO orders (contractor_id, object_id, type_of_work_id, user_id, materials, customer_price, area, cost, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            contractor_id, object_id, type_of_work_id, user_id,
            ','.join(materials.keys()), customer_price, area, cost, 'В обработке'
        ))
        db.commit()

        return jsonify({'status': 'success', 'message': 'Заказ успешно создан!'})

    except ValueError as e:
        return jsonify({'status': 'error', 'message': f'Неверный формат данных: {e}'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/view_orders', methods=['GET'])
def view_orders():
    try:
        cursor.execute("""
            SELECT o.id, u.id AS user_id, u.login AS user, c.name AS contractor, 
                   o.materials, ob.name AS object, tw.name AS work_type,
                   o.customer_price, o.area, o.cost, o.status
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN contractors c ON o.contractor_id = c.id
            JOIN objects ob ON o.object_id = ob.id
            JOIN types_of_work tw ON o.type_of_work_id = tw.id
        """)
        orders = cursor.fetchall()
        return jsonify(convert_decimal(orders))
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/user_orders', methods=['GET'])
def user_orders():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID required'}), 400
    try:
        cursor.execute("""
            SELECT o.id, u.id AS user_id, u.login AS user, c.name AS contractor, 
                   o.materials, ob.name AS object, tw.name AS work_type,
                   tw.multiplier, o.customer_price, o.area, o.cost, o.status
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN contractors c ON o.contractor_id = c.id
            JOIN objects ob ON o.object_id = ob.id
            JOIN types_of_work tw ON o.type_of_work_id = tw.id
            WHERE o.user_id = %s
        """, (user_id,))
        orders = cursor.fetchall()
        return jsonify({'status': 'success', 'orders': convert_decimal(orders)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/get_order_details', methods=['GET'])
def get_order_details():
    order_id = request.args.get('order_id')
    if not order_id:
        return jsonify({'status': 'error', 'message': 'Order ID required'}), 400
    try:
        cursor.execute("""
            SELECT o.id, o.contractor_id, o.object_id, o.type_of_work_id, o.user_id,
                   o.materials, o.customer_price, o.area, o.cost, o.status,
                   c.name AS contractor, ob.name AS object, tw.name AS work_type, tw.multiplier
            FROM orders o
            JOIN contractors c ON o.contractor_id = c.id
            JOIN objects ob ON o.object_id = ob.id
            JOIN types_of_work tw ON o.type_of_work_id = tw.id
            WHERE o.id = %s
        """, (order_id,))
        order = cursor.fetchone()
        if not order:
            return jsonify({'status': 'error', 'message': 'Заказ не найден'}), 404
        order['materials'] = order['materials'].split(',') if order['materials'] else []
        return jsonify({'status': 'success', 'order': convert_decimal(order)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/update_order', methods=['POST'])
def update_order():
    try:
        data = request.json
        order_id = data.get('order_id')
        user_id = data.get('user_id')
        if not order_id or not user_id:
            return jsonify({'status': 'error', 'message': 'Order ID and User ID required'}), 400

        # Проверяем роль пользователя
        cursor.execute("SELECT role FROM users WHERE id = %s", (user_id,))
        user_role = cursor.fetchone()['role']

        # Если не админ, проверяем принадлежность заказа
        if user_role != 'admin':
            cursor.execute("SELECT user_id FROM orders WHERE id = %s", (order_id,))
            order = cursor.fetchone()
            if not order or order['user_id'] != user_id:
                return jsonify({'status': 'error', 'message': 'Доступ запрещен'}), 403

        # Обновление данных заказа
        contractor = data.get('contractor')
        materials = {k: float(v) for k, v in data.get('materials', {}).items()}
        obj = data.get('object')
        work_type = data.get('work_type')
        customer_price = float(data.get('customer_price'))
        area = float(data.get('area'))

        cursor.execute("SELECT id FROM contractors WHERE name = %s", (contractor,))
        contractor_id = cursor.fetchone()['id']

        cursor.execute("SELECT id FROM objects WHERE name = %s", (obj,))
        object_id = cursor.fetchone()['id']

        cursor.execute("SELECT id, multiplier FROM types_of_work WHERE name = %s", (work_type,))
        type_of_work = cursor.fetchone()
        type_of_work_id = type_of_work['id']
        multiplier = float(type_of_work['multiplier'])

        material_cost = sum(materials.values())
        cost = material_cost + (multiplier * customer_price * area)

        cursor.execute("""
            UPDATE orders
            SET contractor_id = %s, object_id = %s, type_of_work_id = %s,
                materials = %s, customer_price = %s, area = %s, cost = %s
            WHERE id = %s
        """, (
            contractor_id, object_id, type_of_work_id,
            ','.join(materials.keys()), customer_price, area, cost, order_id
        ))
        db.commit()
        return jsonify({'status': 'success', 'message': 'Заказ обновлен успешно!'})

    except ValueError as e:
        return jsonify({'status': 'error', 'message': f'Неверный формат данных: {e}'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/update_status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    try:
        data = request.json
        new_status = data.get('status')

        if not new_status:
            return jsonify({'status': 'error', 'message': 'Не указан статус'}), 400

        # Проверяем, существует ли такой статус
        cursor.execute("SELECT status FROM order_statuses WHERE status = %s", (new_status,))
        if not cursor.fetchone():
            return jsonify({'status': 'error', 'message': 'Недопустимый статус'}), 400

        # Получаем данные о заказе
        cursor.execute("SELECT user_id FROM orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()
        if not order:
            return jsonify({'status': 'error', 'message': 'Заказ не найден'}), 404

        # Проверяем права пользователя
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'User ID required'}), 400

        cursor.execute("SELECT role FROM users WHERE id = %s", (user_id,))
        user_role = cursor.fetchone()['role']

        if user_role != 'admin':
            # Обычный пользователь может менять только свои заказы
            if order['user_id'] != user_id:
                return jsonify({'status': 'error', 'message': 'Доступ запрещен'}), 403

        # Обновляем статус
        cursor.execute("UPDATE orders SET status = %s WHERE id = %s", (new_status, order_id))
        db.commit()

        return jsonify({'status': 'success', 'message': 'Статус обновлен!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/add_material', methods=['POST'])
def add_material():
    try:
        data = request.json
        name = data.get('name')
        price = float(data.get('price'))

        if not name or price <= 0:
            return jsonify({'status': 'error', 'message': 'Некорректные данные'}), 400

        cursor.execute("INSERT INTO materials (name, price) VALUES (%s, %s)", (name, price))
        db.commit()
        return jsonify({'status': 'success', 'message': 'Материал успешно добавлен!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/add_contractor', methods=['POST'])
def add_contractor():
    try:
        data = request.json
        name = data.get('name')

        if not name:
            return jsonify({'status': 'error', 'message': 'Некорректные данные'}), 400

        cursor.execute("INSERT INTO contractors (name) VALUES (%s)", (name,))
        db.commit()
        return jsonify({'status': 'success', 'message': 'Подрядчик успешно добавлен!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/load_statuses', methods=['GET'])
def load_statuses():
    try:
        cursor.execute("SELECT status FROM order_statuses")
        statuses = [row['status'] for row in cursor.fetchall()]
        return jsonify({'status': 'success', 'statuses': statuses})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/delete_order/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'status': 'error', 'message': 'User ID required'}), 400

        # Проверяем существование заказа
        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()
        if not order:
            return jsonify({'status': 'error', 'message': 'Заказ не найден'}), 404

        # Проверяем права пользователя
        cursor.execute("SELECT role FROM users WHERE id = %s", (user_id,))
        user_role = cursor.fetchone()['role']

        if user_role != 'admin':
            if order['user_id'] != user_id:
                return jsonify({'status': 'error', 'message': 'Доступ запрещен'}), 403

        # Удаляем заказ
        cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
        db.commit()

        return jsonify({'status': 'success', 'message': 'Заказ успешно удален'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(port=80, debug=True)