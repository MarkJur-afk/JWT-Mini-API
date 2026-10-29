import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# secret is in .env file, not here in the code
load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
if JWT_SECRET is None:
    raise RuntimeError("JWT_SECRET not found in .env")

app = Flask(__name__)

# just two users in a dict, task says no database
USERS = {
    "student": {"password": "student123", "role": "student"},
    "admin": {"password": "admin123", "role": "admin"},
}


@app.route("/login", methods=["POST"])
def login():
    # username and password come in the json
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    # wrong username or wrong password -> 401
    user = USERS.get(username)
    if user is None or user["password"] != password:
        return jsonify({"error": "Wrong username or password"}), 401

    # data inside the token
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,                    # who the token is for
        "role": user["role"],
        "iat": now,                         # time when created
        "exp": now + timedelta(minutes=5),  # dies after 5 minutes
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return jsonify({"token": token}), 200


# I use this function in /profiil and in /admin so I dont repeat the code
# if token is ok it gives (payload, None), if not then (None, error text)
def check_token():
    auth_header = request.headers.get("Authorization", "")

    # no header or its not Bearer -> no token
    if not auth_header.startswith("Bearer "):
        return None, "Token is missing"

    # cut the word "Bearer " away, only token stays
    token = auth_header[len("Bearer "):]

    try:
        # jwt.decode checks the signature and also if token is expired
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        # this must be before InvalidTokenError
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
    payload, error = check_token()
    if error:
        return jsonify({"error": error}), 401

    # token is fine but user is not admin, so 403 and not 401
    if payload["role"] != "admin":
        return jsonify({"error": "Admin access only"}), 403

    return jsonify({"message": "Welcome, admin!"}), 200


if __name__ == "__main__":
    # not 5000 because mac uses it for AirPlay
    app.run(debug=True, port=5001)
