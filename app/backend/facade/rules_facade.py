from flask import Blueprint, jsonify
import json

rules_bp = Blueprint("rules", __name__)

@rules_bp.route("/api/rules", methods=["GET"])
def get_rules():
    # Ouvrir le fichier json
    with open("../frontend/static/data/consignes.json", "r", encoding="utf-8") as f:
        #json.load()
        data = json.load(f)
    #return jsonify
    return jsonify(data)
