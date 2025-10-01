from datetime import datetime, timezone
from db.models import User
from utils.validators import is_valid_email, is_valid_password

class AuthService:

    def __init__(self, db, security, config):
        self.db = db # db = SQLAlchemy()
        self.security = security
        self.config = config

    def register_user(self, username, email, password):
        if username == "" or len(username) < 3 or len(username) > 50:
            return {"success": False, "message": "Nom d'utilisateur invalide"}

        if not is_valid_email(email):
            return {"success": False, "message": "Email invalide"}

        if not is_valid_password(password):
            return {"success": False, "message": "Mot de passe trop court (minimum 8 caractères)"}

        # Vérifications unicité DB
        if User.query.filter_by(username=username).first():
            return {"success": False, "message": "Nom d'utilisateur déjà utilisé"}

        if User.query.filter_by(email=email).first():
            return {"success": False, "message": "Email déjà utilisé"}

        # Préparation données
        password_hash = self.security.hash_password(password)
        nouvel_utilisateur = User(
            username=username,
            email=email,
            password_hash=password_hash,
            created_at=datetime.now(timezone.utc)
        )

        # Sauvegarde DB
        self.db.session.add(nouvel_utilisateur)
        self.db.session.commit()

        return {
            "success": True,
            "data": {
                "id": nouvel_utilisateur.id,
                "username": nouvel_utilisateur.username,
                "email": nouvel_utilisateur.email,
                "created_at": nouvel_utilisateur.created_at.isoformat()
            }
        }

    def login_user(self, email, password):
        if email == "" or password == "":
            return {"success": False, "message": "Email ou mot de passe manquant"}

        utilisateur = User.query.filter_by(email=email).first()
        if not utilisateur:
            return {"success": False, "message": "Email introuvable"}

        if not self.security.verify_password(password, utilisateur.password_hash):
            return {"success": False, "message": "Mot de passe incorrect"}

        token = self.security.create_token(
            {"id": utilisateur.id, "username": utilisateur.username},
            self.config.SECRET_KEY,
            self.config.JWT_EXP_MINUTES
        )

        return {
            "success": True,
            "data": {
                "token": token,
                "user": {
                    "id": utilisateur.id,
                    "username": utilisateur.username,
                    "email": utilisateur.email,
                }
            }
        }

    def get_user_by_id(self, token):
        if not token:
            return {"success": False, "message": "Token manquant"}

        payload = self.security.decode_token(token, self.config.SECRET_KEY)
        if payload is None:
            return {"success": False, "message": "Token invalide ou expiré"}

        utilisateur = User.query.filter_by(id=payload["id"]).first()
        if not utilisateur:
            return {"success": False, "message": "Utilisateur introuvable"}

        return {
            "success": True,
            "data": {
                "id": utilisateur.id,
                "username": utilisateur.username,
                "email": utilisateur.email,
                "created_at": utilisateur.created_at.isoformat()
            }
        }

    def logout_user(self, token=None):
        return {"success": True, "message": "Déconnexion réussie"}
