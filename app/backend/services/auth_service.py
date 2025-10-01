from datetime import datetime, timezone
from app.backend.db.models import User
from utils.validators import is_valid_email, is_valid_password

class AuthService:

    def __init__(self, db_session, security, config):
        self.db = db_session # Interaction db
        self.security = security # hash + vérif mdp
        self.config = config # secret key + durée token

    def register_user(self, username, email, password):

        # Vérification de base
        if username == "" or len(username) < 3 or len(username) > 50:
            return {"erreur": "Nom d'utilisateur invalide"}

        if not is_valid_email(email):
            return {"erreur": "Email invalide"}

        if not is_valid_password(password):
            return {"erreur": "Mot de passe trop court (minimum 8 caractères)"}

        # Vérifications unicité DB
        utilisateur_by_name = self.db.query(User).filter_by(username=username).first()
        if utilisateur_by_name:
            return {"erreur": "Nom d'utilisateur déjà utilisé"}

        utilisateur_by_email = self.db.query(User).filter_by(email=email).first()
        if utilisateur_by_email:
            return {"erreur": "Email déjà utilisé"}

        # Préparation données
        password_hash = self.security.hash_password(password)

        nouvel_utilisateur = User(
            username = username,
            email = email,
            password_hash = password_hash,
            created_at = datetime.now(timezone.utc)
        )

        # Sauvegarder en DB
        self.db.add(nouvel_utilisateur)
        self.db.commit()

        # Réponse simplifiée
        return {
            "id": nouvel_utilisateur.id,
            "username": nouvel_utilisateur.username,
            "email": nouvel_utilisateur.email,
            "created_at": nouvel_utilisateur.created_at.isoformat()
        }
