from flask import Blueprint, jsonify, request

auth_bp = Blueprint("auth", __name__)
# On déclarera auth_service plus tard via app.py
auth_service = None

def init_auth_routes(service):
    global auth_service
    auth_service = service

@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    response = auth_service.register_user(
        username=data.get("username"),
        email=data.get("email"),
        password=data.get("password")
    )
    return jsonify(response)


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    response = auth_service.login_user(
        email=data.get("email"),
        password=data.get("password")
    )
    return jsonify(response)


@auth_bp.route("/api/me", methods=["GET"])
def me():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"success": False, "message": "Token manquant"}), 401

    token = auth_header.split(" ")[1] # "Bearer <token>"
    response = auth_service.get_user_by_id(token)
    return jsonify(response)


@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    response = auth_service.logout_user()
    return jsonify(response)
