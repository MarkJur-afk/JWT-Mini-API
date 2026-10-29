import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Читаем файл .env (там лежит JWT_SECRET)
load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
if JWT_SECRET is None:
    raise RuntimeError("JWT_SECRET не найден в .env")

app = Flask(__name__)

# Наши "пользователи" (база данных не нужна)
USERS = {
    "student": {"password": "student123", "role": "student"},
    "admin": {"password": "admin123", "role": "admin"},
}


@app.route("/login", methods=["POST"])
def login():
    # Берём username и password из JSON, который прислал клиент
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    # Проверяем: такой пользователь есть и пароль совпадает?
    user = USERS.get(username)
    if user is None or user["password"] != password:
        return jsonify({"error": "Wrong username or password"}), 401

    # Создаём JWT: sub, role, iat, exp
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,                    # кто это
        "role": user["role"],               # его роль
        "iat": now,                         # когда выдан
        "exp": now + timedelta(minutes=5),  # когда истекает (через 5 минут)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return jsonify({"token": token}), 200


if __name__ == "__main__":
    # Порт 5001, потому что на Mac порт 5000 занят AirPlay
    app.run(debug=True, port=5001)
