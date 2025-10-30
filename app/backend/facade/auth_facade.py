from flask import Blueprint, config, jsonify, make_response, request, current_app

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

    # Lire uniquement depuis les cookies
    token = request.cookies.get("access_token")

    if not token:
        return jsonify({"success": False, "message": "Token manquant"}), 401

    response = service.get_user_by_id(token)
    return jsonify(response), response["status_code"]


@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    """
    Déconnecte l'utilisateur en supprimant les cookies de tokens
    """

    response = make_response(jsonify({
        "success": True,
        "message": "Déconnexion réussie"
    }), 200)

    # Supprimer access_token avec les MÊMES attributs que lors de la création
    response.set_cookie(
        'access_token',
        value='',
        max_age=0,
        httponly=True,
        secure=False,
        samesite='Lax',
        path='/'
    )

    # Supprimer refresh_token avec les MÊMES attributs
    response.set_cookie(
        'refresh_token',
        value='',
        max_age=0,
        httponly=True,
        secure=False,
        samesite='Lax',
        path='/'
    )

    return response

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
