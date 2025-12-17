from flask import Blueprint, jsonify, request, current_app
from db.models import Score
from utils.auth_utils import verify_token_and_get_user_id


score_bp = Blueprint("score", __name__)

@score_bp.route("/api/scores", methods=["POST"])
def add_scores():

    # Vérification token et récupération user_id
    user_id, error = verify_token_and_get_user_id()
    if error:
        return jsonify(error), error["status_code"]

    # Logique métier : enregistrement du score
    score_service = current_app.config["services"]["score"]
    badge_service = current_app.config["services"]["badge"]
    data = request.get_json()

    response = score_service.add_score(
        user_id=user_id,
        points=data.get("points"),
        correct_items=data.get("correct_items"),
        total_items=data.get("total_items"),
        duration_ms=data.get("duration_ms")
        )

    # Debug
    print(f"🔍 Response success: {response.get('success')}")

    if response.get("success"):
        print(f"🔍 Avant check_and_award_badges pour user {user_id}")
        score_id = response["data"]["score_id"]
        score_obj = Score.query.get(score_id)
        print(f"🔍 Score object: {score_obj}, points: {score_obj.points if score_obj else 'None'}")

        # Appel du badge service
        badge_result = badge_service.check_and_award_badges(user_id, score_obj)
        print(f"🔍 Badge result: {badge_result}")

    return jsonify(response), response["status_code"]

@score_bp.route("/api/scores/me", methods=["GET"])
def user_score():
    # Vérification token et récupération user_id
    user_id, error = verify_token_and_get_user_id()
    if error:
        return jsonify(error), error["status_code"]

    score_service = current_app.config["services"]["score"]
    response = score_service.get_user_scores(user_id)
    return jsonify(response), response["status_code"]

@score_bp.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    score_service = current_app.config["services"]["score"]
    limit = request.args.get("limit", default=15, type=int)

    response = score_service.get_leaderboard(limit)
    return jsonify(response), response["status_code"]

@score_bp.route("/api/stats/me", methods=["GET"])
def get_my_stats():
    """
    Route pour récupérer les statistiques de l'utilisateur connecté.
    Nécessite un token JWT valide dans les cookies.
    """
    # Vérification token et récupération user_id
    user_id, error = verify_token_and_get_user_id()
    if error:
        return jsonify(error), error["status_code"]

    # 1. Récupérer les services
    score_service = current_app.config["services"]["score"]

    # 2. Appeler la fonction du service pour obtenir les stats
    stats = score_service.get_user_stats(user_id)

    # 3. Return direct sur le résultat
    return jsonify(stats), stats["status_code"]
