from flask import Blueprint, jsonify, request, current_app
from utils.auth_utils import verify_token_and_get_user_id
badge_bp = Blueprint("badge", __name__)

@badge_bp.route("/api/badges/me", methods=["GET"])
def user_badges():
        # Vérification token et récupération user_id
    user_id, error = verify_token_and_get_user_id()
    if error:
        return jsonify(error), error["status_code"]

    badge_service = current_app.config["services"]["badge"]
    response = badge_service.get_user_badges(user_id)
    return jsonify(response), response["status_code"]

@badge_bp.route("/api/badges", methods=["GET"])
def all_badges():
    badge_service = current_app.config["services"]["badge"]
    response = badge_service.get_all_badges()
    return jsonify(response), response["status_code"]
