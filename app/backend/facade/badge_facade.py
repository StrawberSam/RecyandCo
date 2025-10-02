from flask import Blueprint, jsonify, request

badge_bp = Blueprint("badge", __name__)

auth_service = None
badge_service = None

def init_badge_routes(auth_srv, badge_srv):
    global auth_service, badge_service
    auth_service = auth_srv
    badge_service = badge_srv

@badge_bp.route("/api/badges/me", methods=["GET"])
def user_badges():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"success": False, "message": "Token manquant"}), 401

    token = auth_header.split(" ")[1]
    user = auth_service.get_user_by_id(token) # Récupère id par le token

    if not user.get("success"): # si problème avec le token
        return jsonify(user), 401

    user_id = user["data"]["id"]
    response = badge_service.get_user_badges(user_id)
    return jsonify(response)

@badge_bp.route("/api/badges", methods=["GET"])
def all_badges():
    response = badge_service.get_all_badges()
    return jsonify(response)
