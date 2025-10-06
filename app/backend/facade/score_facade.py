from flask import Blueprint, jsonify, request, current_app

score_bp = Blueprint("score", __name__)

@score_bp.route("/api/scores", methods=["POST"])
def add_scores():
    score_service = current_app.config["services"]["score"]
    data = request.get_json()
    response = score_service.add_score(
        user_id=data.get("user_id"),
        points=data.get("points")
        )
    return jsonify(response), response["status_code"]

@score_bp.route("/api/scores/me", methods=["GET"])
def user_score():
    auth_service = current_app.config["services"]["auth"]
    score_service = current_app.config["services"]["score"]

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"success": False, "message": "Token manquant"}), 401

    token = auth_header.split(" ")[1]
    user = auth_service.get_user_by_id(token)
    if not user.get("success"):
        return jsonify(user), 401

    user_id = user["data"]["id"]
    response = score_service.get_user_scores(user_id)
    return jsonify(response), response["status_code"]

@score_bp.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    score_service = current_app.config["services"]["score"]
    limit = request.args.get("limit", default=15, type=int)

    response = score_service.get_leaderboard(limit)
    return jsonify(response), response["status_code"]
