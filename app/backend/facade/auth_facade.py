from flask import Blueprint, jsonify, request, current_app

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/register", methods=["POST"])
def register():
    service = current_app.config["services"]["auth"]
    data = request.get_json()
    response = service.register_user(
        username=data.get("username"),
        email=data.get("email"),
        password=data.get("password")
    )
    return jsonify(response), response["status_code"]


@auth_bp.route("/api/login", methods=["POST"])
def login():
    service = current_app.config["services"]["auth"]
    data = request.get_json()
    response = service.login_user(
        email=data.get("email"),
        password=data.get("password")
    )
    return jsonify(response), response["status_code"]


@auth_bp.route("/api/me", methods=["GET"])
def me():
    service = current_app.config["services"]["auth"]
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"success": False, "message": "Token manquant"}), 401

    token = auth_header.split(" ")[1] # "Bearer <token>"
    response = service.get_user_by_id(token)
    return jsonify(response), response["status_code"]


@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    service = current_app.config["services"]["auth"]
    response = service.logout_user()
    return jsonify(response), response["status_code"]

@auth_bp.route("/api/users", methods=["GET"])
def all_users():
    service = current_app.config["services"]["auth"]

    # Récupérer token
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"success": False, "message": "Token manquant"}), 401

    try:
        token = auth_header.split(" ")[1]  # "Bearer <token>"
    except IndexError:
        return jsonify({"success": False, "message": "Format d'Authorization invalide"}), 401

    # Vérifie le token et récupère l’utilisateur
    user_resp = service.get_user_by_id(token)
    if not user_resp.get("success"):
        return jsonify(user_resp), 401

    # Vérifie que l'utilisateur est l'admin défini dans .env
    admin_id = current_app.config.get("ADMIN_ID")
    if user_resp["data"]["id"] != admin_id:
        return jsonify({"success": False, "message": "Accès refusé"}), 403

    # Retourne tous les users (seulement si admin)
    return jsonify(service.get_all_users()), 200
