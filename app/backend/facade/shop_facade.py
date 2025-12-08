from flask import Blueprint, jsonify, request, current_app
from utils.auth_utils import verify_token_and_get_user_id
shop_bp = Blueprint("shop", __name__)

@shop_bp.route("/api/shop/items", methods=["GET"])
def get_shop_items():
    shop_service = current_app.config["services"]["shop"]
    response = shop_service.get_active_items()
    return jsonify(response), response["status_code"]

@shop_bp.route("/api/shop/can_purchase", methods=["POST"])
def can_purchase_item():
    # Vérification du token et récupération de l'user_id
    user_id, error = verify_token_and_get_user_id()
    if error:
        return jsonify(error), error["status_code"]

    # Validation des données de la requête
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Requête invalide : aucun JSON reçu"}), 400

    if "item_id" not in data:
        return jsonify({"success": False, "message": "Champ item_id manquant dans la requête"}), 400

    item_id = data.get("item_id")
    if not isinstance(item_id, int) or item_id <= 0:
        return jsonify({"success": False, "message": "Champ item_id invalide, doit être un entier positif"}), 400

    # Vérification possibilté d'achat
    shop_service = current_app.config["services"]["shop"]
    response = shop_service.can_purchase(user_id, item_id)

    if "success" in response and "status_code" in response:
        return jsonify(response), response["status_code"]
    else:
        return jsonify({"success": False, "message": "Erreur interne lors du traitement de la requête"}), 500

@shop_bp.route("/api/shop/purchase", methods=["POST"])
def purchase_item():
    # Vérification du token et récupération de l'user_id
    user_id, error = verify_token_and_get_user_id()
    if error:
        return jsonify(error), error["status_code"]

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Requête invalide : aucun JSON reçu"}), 400

    # Récupération donnée + vérif
    if "item_id" not in data:
        return jsonify({"success": False, "message": "Champ item_id manquant"}), 400

    item_id = data.get("item_id")
    if not isinstance(item_id, int) or item_id <= 0:
        return jsonify({"success": False, "message": "Champ item_id invalide"}), 400

    # appel du service
    shop_service = current_app.config["services"]["shop"]
    response = shop_service.purchase_item(user_id, item_id)
    return jsonify(response), response["status_code"]
