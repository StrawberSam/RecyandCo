from flask import Blueprint, config, jsonify, make_response, request, current_app
from utils.auth_utils import verify_token_and_get_user_id, set_auth_cookies, clear_auth_cookies
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
        access_token = response["data"].pop("access_token")
        refresh_token = response["data"].pop("refresh_token")

        flask_response = make_response(jsonify(response), 200)

        # Utilisation de l'utilitaire pour configurer les cookies
        set_auth_cookies(flask_response, access_token, refresh_token)

        return flask_response

    return jsonify(response), response["status_code"]


@auth_bp.route("/api/me", methods=["GET"])
def me():
    # Vérification du token et récupération de l'user_id
    user_id, error = verify_token_and_get_user_id()
    if error:
        return jsonify(error), error["status_code"]

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

    # Utilisation utilitaire pour supprimer les cookies
    clear_auth_cookies(response)
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
        set_auth_cookies(response, new_access_token)
    return response
