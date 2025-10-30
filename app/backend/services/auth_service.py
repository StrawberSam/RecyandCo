"""
Service d'authentification pour Récy&Co.

Ce module gère toute la logique d'authentification de l'application :
inscription, connexion, gestion des tokens JWT, et récupération des
informations utilisateur.

Classes:
    AuthService: Service principal pour l'authentification des utilisateurs

Author: Roche Samira
Project: Récy&Co - Sorting is fun!
"""

from datetime import datetime, timezone
from db.models import User
from utils.validators import is_valid_email, is_valid_password

class AuthService:
    """
    Service gérant l'authentification et la gestion des utilisateurs.

    Ce service encapsule toute la logique liée à l'authentification :
    - Inscription de nouveaux utilisateurs
    - Connexion et génération de tokens JWT
    - Validation et décodage des tokens
    - Rafraîchissement des tokens d'accès

    Attributes:
        db: Instance de SQLAlchemy pour les opérations de base de données
        security: Service de sécurité pour le hashage et les tokens JWT
        config: Configuration de l'application (clés secrètes, durées d'expiration)
    """

    def __init__(self, db, security, config):
        """
        Initialise le service d'authentification.

        Args:
            db: Instance SQLAlchemy pour les accès à la base de données
            security: Service de sécurité (hashage mot de passe, JWT)
            config: Objet de configuration (SECRET_KEY, JWT_EXP_MINUTES, etc.)
        """
        self.db = db # db = SQLAlchemy()
        self.security = security
        self.config = config

    def register_user(self, username, email, password):
        """
        Inscrit un nouvel utilisateur dans l'application.

        Cette méthode effectue plusieurs validations avant de créer l'utilisateur :
        - Vérifie la longueur et le format du nom d'utilisateur (3-50 caractères)
        - Vérifie le format de l'email
        - Vérifie la robustesse du mot de passe (minimum 8 caractères)
        - Vérifie l'unicité du nom d'utilisateur et de l'email

        Args:
            username (str): Nom d'utilisateur souhaité (3-50 caractères)
            email (str): Adresse email de l'utilisateur (doit être valide et unique)
            password (str): Mot de passe en clair (minimum 8 caractères)

        Returns:
            dict: Dictionnaire contenant :
                - success (bool): True si l'inscription a réussi
                - data (dict): Informations de l'utilisateur créé (id, username, email, created_at)
                  OU
                - message (str): Message d'erreur si échec
                - status_code (int): Code HTTP approprié
                    - 201 : Utilisateur créé avec succès
                    - 400 : Données invalides
                    - 409 : Conflit (username ou email déjà utilisé)
        """

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
        """
        Authentifie un utilisateur et génère des tokens JWT.

        Cette méthode vérifie les identifiants de l'utilisateur et, en cas
        de succès, génère deux tokens :
        - Un access token (courte durée, pour les requêtes API)
        - Un refresh token (longue durée, pour renouveler l'access token)

        Args:
            email (str): Adresse email de l'utilisateur
            password (str): Mot de passe en clair

        Returns:
            dict: Dictionnaire contenant :
                - success (bool): True si la connexion a réussi
                - data (dict): Contient les tokens et informations utilisateur :
                    - access_token (str): Token JWT d'accès (1h par défaut)
                    - refresh_token (str): Token JWT de rafraîchissement (7j par défaut)
                    - user (dict): Informations basiques (id, username)
                  OU
                - message (str): Message d'erreur si échec
                - status_code (int): Code HTTP approprié
                    - 200 : Connexion réussie
                    - 400 : Données manquantes
                    - 401 : Mot de passe incorrect
                    - 404 : Email introuvable
        """

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
        """
        Récupère les informations d'un utilisateur à partir de son token JWT.

        Cette méthode décode le token, extrait l'ID utilisateur, et récupère
        les informations complètes de l'utilisateur depuis la base de données.

        Args:
            token (str): Token JWT d'accès de l'utilisateur

        Returns:
            dict: Dictionnaire contenant :
                - success (bool): True si l'opération a réussi
                - data (dict): Informations complètes de l'utilisateur :
                    - id (int): Identifiant de l'utilisateur
                    - username (str): Nom d'utilisateur
                    - email (str): Adresse email
                    - created_at (str): Date de création (format ISO)
                    - total_score (int): Score total accumulé
                  OU
                - message (str): Message d'erreur si échec
                - status_code (int): Code HTTP approprié
                    - 200 : Utilisateur trouvé
                    - 401 : Token manquant, invalide ou expiré
                    - 404 : Utilisateur introuvable

        Note:
            Cette méthode est utilisée pour récupérer le profil de l'utilisateur
            connecté. Elle nécessite un token JWT valide.
        """

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

    def refresh_access_token(self, refresh_token):
        """
        Génère un nouveau token d'accès à partir d'un refresh token valide.

        Lorsque l'access token expire (après 1h par défaut), cette méthode
        permet d'en obtenir un nouveau sans redemander à l'utilisateur de
        se reconnecter, en utilisant le refresh token (valide 7 jours).

        Args:
            refresh_token (str): Token JWT de rafraîchissement

        Returns:
            dict: Dictionnaire contenant :
                - success (bool): True si le renouvellement a réussi
                - message (str): Message de confirmation
                - data (dict): Contient le nouveau token :
                    - access_token (str): Nouveau token JWT d'accès (1h)
                  OU
                - message (str): Message d'erreur si échec
                - status_code (int): Code HTTP approprié
                    - 200 : Nouveau token généré avec succès
                    - 401 : Refresh token invalide ou expiré
        """

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
