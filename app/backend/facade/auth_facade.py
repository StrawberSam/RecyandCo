from flask import Blueprint, jsonify, make_response, request, current_app

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

    # Si connexion réussie → stocker les tokens dans des cookies sécurisés
    if response.get("success"):
        # Stocker aussi l'access_token dans un cookie
        access_token = response["data"].pop("access_token")
        refresh_token = response["data"].pop("refresh_token")

        flask_response = make_response(jsonify(response), 200)

        # Cookie access_token (courte durée)
        flask_response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=60*60  # 1 heure
        )

        # Cookie refresh_token (longue durée)
        flask_response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=60*60*24*7  # 7 jours
        )

        return flask_response

    return jsonify(response), response["status_code"]


@auth_bp.route("/api/me", methods=["GET"])
def me():
    service = current_app.config["services"]["auth"]

    # ✅ CORRECTION : Lire uniquement depuis les cookies
    token = request.cookies.get("access_token")

    if not token:
        return jsonify({"success": False, "message": "Token manquant"}), 401

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

    # ✅ CORRECTION : Lire depuis les cookies
    token = request.cookies.get("access_token")

    if not token:
        return jsonify({"success": False, "message": "Token manquant"}), 401

    # Vérifie le token et récupère l'utilisateur
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

    result = service.refresh_access_token(refresh_token)

    if not result.get("success"):
        return jsonify(result), result.get("status_code", 401)

    response = make_response(jsonify({
        "success": True,
        "message": "Token rafraîchi"
    }), 200)

    # Extrait nouveau access_token
    new_access_token = result.get("data", {}).get("access_token")

    # Met le nouveau access_token dans un cookie
    if new_access_token:
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            path='/',
            max_age=3600
        )
    return response
