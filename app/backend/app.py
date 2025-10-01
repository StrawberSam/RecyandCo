from dotenv import load_dotenv
load_dotenv()  # Charge le fichier .env

from flask import Flask, request, jsonify
from db import db
from config import config
from utils import security
from services.auth_service import AuthService

# Initialisation de l’app Flask
app = Flask(__name__)

# Récupération de la config (par défaut : development)
app_config = config["development"]()
app.config.from_object(app_config)

# Initialisation de la DB avec Flask
db.init_app(app)

# Importer les modèles (important pour db.create_all())
from db import models

with app.app_context():
    db.create_all()

# Instanciation du service d’auth
auth_service = AuthService(db, security, app_config)

# -------------------- ROUTES --------------------

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    response = auth_service.register_user(
        username=data.get("username"),
        email=data.get("email"),
        password=data.get("password")
    )
    return jsonify(response)


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    response = auth_service.login_user(
        email=data.get("email"),
        password=data.get("password")
    )
    return jsonify(response)


@app.route("/api/me", methods=["GET"])
def me():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"success": False, "message": "Token manquant"}), 401

    token = auth_header.split(" ")[1]  # "Bearer <token>"
    response = auth_service.get_user_by_id(token)
    return jsonify(response)


@app.route("/api/logout", methods=["POST"])
def logout():
    response = auth_service.logout_user()
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
