from flask import Blueprint, jsonify, request, current_app

score_bp = Blueprint("score", __name__)

@score_bp.route("/api/scores", methods=["POST"])
def add_scores():
    auth_service = current_app.config["services"]["auth"]
    score_service = current_app.config["services"]["score"]

    token = request.cookies.get("access_token")
    if not token:
        return jsonify({"success": False, "message": "Token manquant"}), 401

    user = auth_service.get_user_by_id(token)
    if not user.get("success"):
        return jsonify(user), 401

    user_id = user["data"]["id"]

    data = request.get_json()
    response = score_service.add_score(
        user_id=user_id,
        points=data.get("points")
        )
    return jsonify(response), response["status_code"]

@score_bp.route("/api/scores/me", methods=["GET"])
def user_score():
    auth_service = current_app.config["services"]["auth"]
    score_service = current_app.config["services"]["score"]

    token = request.cookies.get("access_token")
    if not token:
        return jsonify({"success": False, "message": "Token manquant"}), 401
    
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

@score_bp.route("/api/stats/me", methods=["GET"])
def get_my_stats():
    """
    Route pour récupérer les statistiques de l'utilisateur connecté.
    Nécessite un token JWT valide dans les cookies.
    """
    # 1. Récupérer les services
    auth_service = current_app.config["services"]["auth"]
    score_service = current_app.config["services"]["score"]

    # 2. Récupérer le token depuis les COOKIES
    token = request.cookies.get("access_token")
    if not token:
        return jsonify({
            "success": False,
            "message": "Token manquant"
        }), 401

    # 3. Vérifier le token et récupérer l'utilisateur
    user = auth_service.get_user_by_id(token)
    if not user.get("success"):
        return jsonify(user), 401

    # 4. Récupérer l'user_id
    user_id = user["data"]["id"]

    try:
        # 5. Appeler la fonction du service pour obtenir les stats
        stats = score_service.get_user_stats(user_id)

        # 6. Renvoyer les stats en JSON avec succès
        return jsonify({
            "success": True,
            "data": stats
        }), 200

    except Exception as e:
        # En cas d'erreur, renvoyer un message d'erreur
        return jsonify({
            "success": False,
            "message": "Erreur lors de la récupération des statistiques",
            "error": str(e)
        }), 500
