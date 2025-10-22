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
            return {"success": False, "message": "Nom d'utilisateur invalide", "status_code": 400}

        if not is_valid_email(email):
            return {"success": False, "message": "Email invalide", "status_code": 400}

        if not is_valid_password(password):
            return {"success": False, "message": "Mot de passe trop court (minimum 8 caractères)", "status_code": 400}

        # Vérifications unicité DB
        if User.query.filter_by(username=username).first():
            return {"success": False, "message": "Nom d'utilisateur déjà utilisé", "status_code": 409}

        if User.query.filter_by(email=email).first():
            return {"success": False, "message": "Email déjà utilisé", "status_code": 409}

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
            },
            "status_code": 201
        }

    def login_user(self, email, password):
        if email == "" or password == "":
            return {"success": False, "message": "Email ou mot de passe manquant", "status_code": 400}

        utilisateur = User.query.filter_by(email=email).first()
        if not utilisateur:
            return {"success": False, "message": "Email introuvable", "status_code": 404}

        if not self.security.verify_password(password, utilisateur.password_hash):
            return {"success": False, "message": "Mot de passe incorrect", "status_code": 401}

        # === Génération des deux tokens ===
        access_token = self.security.create_token(
            {"id": utilisateur.id, "username": utilisateur.username},
            self.config.SECRET_KEY,
            self.config.JWT_EXP_MINUTES
        )

        refresh_token = self.security.create_token(
            {"id": utilisateur.id},
            self.config.SECRET_KEY,
            expiration_minutes=self.config.JWT_REFRESH_EXP_MINUTES
        )

        return {
            "success": True,
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": utilisateur.id,
                    "username": utilisateur.username
                }
            },
            "status_code": 200
        }

    def get_user_by_id(self, token):
        if not token:
            return {"success": False, "message": "Token manquant", "status_code": 401}

        payload = self.security.decode_token(token, self.config.SECRET_KEY)
        if payload is None:
            return {"success": False, "message": "Token invalide ou expiré", "status_code": 401}

        utilisateur = User.query.filter_by(id=payload["id"]).first()
        if not utilisateur:
            return {"success": False, "message": "Utilisateur introuvable", "status_code": 404}

        return {
            "success": True,
            "data": {
                "id": utilisateur.id,
                "username": utilisateur.username,
                "email": utilisateur.email,
                "created_at": utilisateur.created_at.isoformat(),
                "total_score": utilisateur.total_score
            },
            "status_code": 200
        }

    def get_all_users(self):
        utilisateurs = User.query.all()
        return {
            "success": True,
            "data": [
                {
                    "id": u.id,
                    "username": u.username,
                    "email": u.email,
                    "created_at": u.created_at.isoformat()
                }
                for u in utilisateurs
            ],
            "status_code": 200
        }

    def refresh_access_token(self, refresh_token):
        payload = self.security.decode_token(refresh_token, self.config.SECRET_KEY)
        if payload is None:
            return {"success": False, "message": "Token invalide ou expiré", "status_code": 401}

        # On génère un nouveau access token (1h)
        new_access_token = self.security.create_token(
            {"id": payload["id"]},
            self.config.SECRET_KEY,
            expiration_minutes=self.config.JWT_EXP_MINUTES
        )

        return {
            "success": True,
            "message": "Nouveau access token généré",
            "data": {"access_token": new_access_token},
            "status_code": 200
        }
