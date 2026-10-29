import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# load secret key from .env
load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
if JWT_SECRET is None:
    raise RuntimeError("JWT_SECRET not found in .env")

app = Flask(__name__)

# test users, no database needed
USERS = {
    "student": {"password": "student123", "role": "student"},
    "admin": {"password": "admin123", "role": "admin"},
}


@app.route("/login", methods=["POST"])
def login():
    # get username and password from json body
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    # check if user exists and password is correct
    user = USERS.get(username)
    if user is None or user["password"] != password:
        return jsonify({"error": "Wrong username or password"}), 401

    # make the token
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,                    # username
        "role": user["role"],               # student or admin
        "iat": now,                         # issued at
        "exp": now + timedelta(minutes=5),  # expires in 5 min
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return jsonify({"token": token}), 200


# checks the token from Authorization header
# returns (payload, None) if ok, or (None, error message) if not
def check_token():
    auth_header = request.headers.get("Authorization", "")

    # header must be "Bearer <token>"
    if not auth_header.startswith("Bearer "):
        return None, "Token is missing"

    token = auth_header[len("Bearer "):]

    try:
        # decode checks signature and exp
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Token is invalid"

    return payload, None


@app.route("/profiil", methods=["GET"])
def profiil():
    payload, error = check_token()
    if error:
        return jsonify({"error": error}), 401

    return jsonify({"username": payload["sub"], "role": payload["role"]}), 200


@app.route("/admin", methods=["GET"])
def admin():
    # check token first, same as in /profiil
    payload, error = check_token()
    if error:
        return jsonify({"error": error}), 401

    # valid token but not admin -> 403
    if payload["role"] != "admin":
        return jsonify({"error": "Admin access only"}), 403

    return jsonify({"message": "Welcome, admin!"}), 200


if __name__ == "__main__":
    # port 5001 because 5000 is used by AirPlay on mac
    app.run(debug=True, port=5001)
