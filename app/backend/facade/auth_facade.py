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

    # Si connexion réussie → stocker refresh token dans un cookie sécurisé
    if response.get("success"):
        flask_response = jsonify(response)
        refresh_token = response["data"].pop("refresh_token") # on ne renvoie plus le refresh token dans le JSON
        flask_response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True, # non accessible par le JS (anti-XSS)
            secure=True, # obligatoire en HTTPS
            samesite="Lax", # empêche le vol de cookie entre sites
            max_age=60*60*24*7 # 7 jours
        )
        return flask_response, 200

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

@auth_bp.route("/api/refresh", methods=["POST"])
def refresh_token():
    service = current_app.config["services"]["auth"]

    # On récupère le refresh token depuis le cookie
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return jsonify({"success": False, "message": "Refresh token manquant"}), 401

    response = service.refresh_access_token(refresh_token)
    return jsonify(response), response["status_code"]
