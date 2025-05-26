from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/*": {"origins": ["http://localhost:80", "http://localhost"]}})

# Подключение к базе данных
db = mysql.connector.connect(
    host="localhost",
    user="Sashalu",
    password="sashalu",
    database="repair_management"
)
cursor = db.cursor(dictionary=True)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    cursor.execute("SELECT * FROM users WHERE login = %s AND password = %s",
                  (data['login'], data['password']))
    user = cursor.fetchone()
    if user:
        return jsonify({'status': 'success', 'user': user})
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

if __name__ == '__main__':
    app.run(port=5000, debug=True)