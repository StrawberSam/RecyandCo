from flask import Blueprint, jsonify, request, current_app

badge_bp = Blueprint("badge", __name__)

@badge_bp.route("/api/badges/me", methods=["GET"])
def user_badges():
    auth_service = current_app.config["services"]["auth"]
    badge_service = current_app.config["services"]["badge"]

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"success": False, "message": "Token manquant"}), 401

    token = auth_header.split(" ")[1]
    user = auth_service.get_user_by_id(token) # Récupère id par le token

    if not user.get("success"): # si problème avec le token
        return jsonify(user), 401

    user_id = user["data"]["id"]
    response = badge_service.get_user_badges(user_id)
    return jsonify(response), response["status_code"]

@badge_bp.route("/api/badges", methods=["GET"])
def all_badges():
    badge_service = current_app.config["services"]["badge"]
    response = badge_service.get_all_badges()
    return jsonify(response), response["status_code"]
