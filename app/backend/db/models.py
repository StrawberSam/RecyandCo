"""
Module de définition des modèles de base de données pour Récy&Co.

Ce module contient tous les modèles SQLAlchemy représentant la structure
de la base de données du projet éducatif de tri des déchets.

Models:
    User: Représente un utilisateur de l'application
    Score: Enregistre les scores des parties jouées
    Badge: Définit les badges disponibles dans l'application
    UserBadge: Table de liaison entre utilisateurs et badges
    ShopItem: Représente un article de la boutique virtuelle
    UserInventory: Table de liaison entre utilisateurs et articles achetés

Author: Roche Samira
Project: Récy&Co - Sorting is fun!
"""

from sqlalchemy.sql import func
from . import db

# ---------- USER ----------
class User(db.Model):
    """
    Modèle représentant un utilisateur de l'application Récy&Co.

    Un utilisateur peut jouer au jeu de tri, accumuler des scores,
    débloquer des badges et acheter des articles dans la boutique.

    Attributes:
        id (int): Identifiant unique de l'utilisateur (clé primaire)
        username (str): Nom d'utilisateur (max 50 caractères)
        email (str): Adresse email unique (max 255 caractères)
        password_hash (str): Mot de passe hashé (max 255 caractères)
        created_at (datetime): Date et heure de création du compte
        last_login_at (datetime): Date et heure de la dernière connexion (optionnel)
        total_score (int): Score total cumulé de l'utilisateur (par défaut 0)

    Relationships:
        scores (list[Score]): Liste des scores enregistrés par l'utilisateur
        badges (list[UserBadge]): Liste des badges débloqués par l'utilisateur
        inventory (list[UserInventory]): Liste des articles achetés par l'utilisateur
    """
    __tablename__ = "users"

    def __init__(self, **kwargs) -> None:
        """
        Initialise une nouvelle instance d'utilisateur.

        Args:
            **kwargs: Arguments nommés correspondant aux attributs du modèle
        """
        super().__init__(**kwargs)

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)
    total_score = db.Column(db.Integer, default=0, nullable=False)

    # Relations
    scores = db.relationship("Score", back_populates="user")
    badges = db.relationship("UserBadge", back_populates="user")
    inventory = db.relationship("UserInventory", back_populates="user")

    def to_dict(self):
        """
        Convertit l'utilisateur en dictionnaire (avec email).

        Cette méthode est utilisée pour la sérialisation complète de l'utilisateur,
        incluant les informations sensibles comme l'email. À utiliser uniquement
        dans des contextes sécurisés (admin, profil personnel).

        Returns:
            dict: Dictionnaire contenant les informations de l'utilisateur
                - id (int): Identifiant de l'utilisateur
                - username (str): Nom d'utilisateur
                - email (str): Adresse email
                - created_at (datetime): Date de création
                - last_login_at (datetime): Date de dernière connexion
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "last_login_at": self.last_login_at
        }

    def to_public_dict(self):
        """
        Convertit l'utilisateur en dictionnaire public (sans email).

        Cette méthode est utilisée pour partager les informations de l'utilisateur
        dans des contextes publics (classements, profils publics) en excluant
        les données sensibles comme l'email.

        Returns:
            dict: Dictionnaire contenant les informations publiques de l'utilisateur
                - id (int): Identifiant de l'utilisateur
                - username (str): Nom d'utilisateur
                - created_at (datetime): Date de création
                - last_login_at (datetime): Date de dernière connexion
        """
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at,
            "last_login_at": self.last_login_at
        }

# ---------- SCORE ----------
class Score(db.Model):
    """
    Modèle représentant un score de partie au jeu de tri.

    Chaque instance représente une partie jouée par un utilisateur,
    avec les détails de sa performance (items triés, temps, points).

    Attributes:
        id (int): Identifiant unique du score (clé primaire)
        user_id (int): Identifiant de l'utilisateur (clé étrangère)
        points (int): Nombre de points obtenus pendant la partie
        correct_items (int): Nombre d'items correctement triés
        total_items (int): Nombre total d'items présentés
        duration_ms (int): Durée de la partie en millisecondes
        played_at (datetime): Date et heure de la partie

    Relationships:
        user (User): L'utilisateur qui a joué cette partie
    """
    __tablename__ = "scores"

    def __init__(self, **kwargs) -> None:
        """
        Initialise une nouvelle instance de score.

        Args:
            **kwargs: Arguments nommés correspondant aux attributs du modèle
        """
        super().__init__(**kwargs)

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    correct_items = db.Column(db.Integer, nullable=False)
    total_items = db.Column(db.Integer, nullable=False)
    duration_ms = db.Column(db.Integer, nullable=False)
    played_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    # Relations
    user = db.relationship("User", back_populates="scores")

    def efficiency(self):
        """
        Calcule le taux de réussite de la partie.

        Le taux de réussite est le ratio entre le nombre d'items correctement
        triés et le nombre total d'items. Si aucun item n'a été présenté,
        retourne 0 pour éviter une division par zéro.

        Returns:
            float: Taux de réussite entre 0.0 et 1.0
                - 0.0 = aucun item correct ou aucun item total
                - 1.0 = tous les items sont corrects

        Example:
            >>> score = Score(correct_items=8, total_items=10)
            >>> score.efficiency()
            0.8
        """
        return 0 if self.total_items == 0 else self.correct_items / self.total_items

    def to_dict(self):
        """
        Convertit le score en dictionnaire.

        Returns:
            dict: Dictionnaire contenant toutes les informations du score
                - id (int): Identifiant du score
                - points (int): Points obtenus
                - correct_items (int): Nombre d'items corrects
                - total_items (int): Nombre total d'items
                - duration_ms (int): Durée en millisecondes
                - played_at (datetime): Date de la partie
                - efficiency (float): Taux de réussite calculé
        """
        return {
            "id": self.id,
            "points": self.points,
            "correct_items": self.correct_items,
            "total_items": self.total_items,
            "duration_ms": self.duration_ms,
            "played_at": self.played_at,
            "efficiency": self.efficiency()
        }

# ---------- BADGE ----------
class Badge(db.Model):
    """
    Modèle représentant un badge déblocable dans l'application.

    Les badges sont des récompenses que les utilisateurs peuvent débloquer
    en atteignant certains objectifs (seuils de score, nombre de parties, etc.).

    Attributes:
        id (int): Identifiant unique du badge (clé primaire)
        code (str): Code unique du badge (max 50 caractères)
        label (str): Nom du badge affiché à l'utilisateur (max 100 caractères)
        description (str): Description du badge et condition de déblocage
        threshold (int): Seuil requis pour débloquer le badge (optionnel)
        icon (str): Chemin vers l'icône du badge (optionnel, max 255 caractères)

    Relationships:
        users (list[UserBadge]): Liste des utilisateurs ayant débloqué ce badge
    """
    __tablename__ = "badges"

    def __init__(self, **kwargs) -> None:
        """
        Initialise une nouvelle instance de badge.

        Args:
            **kwargs: Arguments nommés correspondant aux attributs du modèle
        """
        super().__init__(**kwargs)

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    label = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    threshold = db.Column(db.Integer, nullable=True)
    icon = db.Column(db.String(255), nullable=True)

    # Relations
    users = db.relationship("UserBadge", back_populates="badge")

    def to_dict(self):
        """
        Convertit le badge en dictionnaire.

        Returns:
            dict: Dictionnaire contenant toutes les informations du badge
                - id (int): Identifiant du badge
                - code (str): Code unique
                - label (str): Nom du badge
                - description (str): Description détaillée
                - threshold (int): Seuil de déblocage
                - icon (str): Chemin de l'icône
        """
        return {
            "id": self.id,
            "code": self.code,
            "label": self.label,
            "description": self.description,
            "threshold": self.threshold,
            "icon": self.icon
        }

# ---------- USERBADGE ----------
class UserBadge(db.Model):
    """
    Modèle de liaison entre utilisateurs et badges (relation many-to-many).

    Cette table enregistre quels badges ont été débloqués par quels utilisateurs,
    ainsi que la date de déblocage.

    Attributes:
        user_id (int): Identifiant de l'utilisateur (clé primaire composée)
        badge_id (int): Identifiant du badge (clé primaire composée)
        awarded_at (datetime): Date et heure du déblocage du badge

    Relationships:
        user (User): L'utilisateur qui a débloqué le badge
        badge (Badge): Le badge qui a été débloqué

    Note:
        La clé primaire est composée de (user_id, badge_id), ce qui signifie
        qu'un utilisateur ne peut débloquer un même badge qu'une seule fois.
    """
    __tablename__ = "user_badges"

    def __init__(self, **kwargs) -> None:
        """
        Initialise une nouvelle instance de liaison utilisateur-badge.

        Args:
            **kwargs: Arguments nommés correspondant aux attributs du modèle
        """
        super().__init__(**kwargs)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), autoincrement=True, primary_key=True, nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey("badges.id"), primary_key=True, nullable=False)
    awarded_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    # Relations
    user = db.relationship("User", back_populates="badges")
    badge = db.relationship("Badge", back_populates="users")

    def to_dict(self):
        """
        Convertit la liaison utilisateur-badge en dictionnaire.

        Returns:
            dict: Dictionnaire contenant les informations du badge débloqué
                - badge_id (int): Identifiant du badge
                - awarded_at (datetime): Date de déblocage
        """
        return {
            "badge_id": self.badge_id,
            "awarded_at": self.awarded_at
        }

# ---------- SHOPITEM ----------
class ShopItem(db.Model):
    """
    Modèle représentant un article dans la boutique virtuelle.

    Les articles peuvent être achetés par les utilisateurs en échange
    de leurs points de score accumulés dans le jeu.

    Attributes:
        id (int): Identifiant unique de l'article (clé primaire)
        sku (str): Code SKU unique de l'article (max 100 caractères)
        name (str): Nom de l'article affiché à l'utilisateur (max 100 caractères)
        price (int): Prix en points de l'article
        is_active (bool): Indique si l'article est disponible à l'achat (par défaut True)

    Relationships:
        users (list[UserInventory]): Liste des utilisateurs ayant acheté cet article

    Note:
        Le champ is_active permet de désactiver temporairement un article
        sans le supprimer de la base de données.
    """
    __tablename__ = "shop_items"

    def __init__(self, **kwargs) -> None:
        """
        Initialise une nouvelle instance d'article de boutique.

        Args:
            **kwargs: Arguments nommés correspondant aux attributs du modèle
        """
        super().__init__(**kwargs)

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    sku = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, server_default="1")

    # Relations
    users = db.relationship("UserInventory", back_populates="item")

    def to_dict(self):
        """
        Convertit l'article en dictionnaire.

        Returns:
            dict: Dictionnaire contenant toutes les informations de l'article
                - id (int): Identifiant de l'article
                - sku (str): Code SKU unique
                - name (str): Nom de l'article
                - price (int): Prix en points
                - is_active (bool): Disponibilité de l'article
        """
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "price": self.price,
            "is_active": self.is_active
        }

# ---------- USERINVENTORY ----------
class UserInventory(db.Model):
    """
    Modèle de liaison entre utilisateurs et articles achetés (relation many-to-many).

    Cette table enregistre quels articles ont été achetés par quels utilisateurs,
    ainsi que la date d'achat.

    Attributes:
        user_id (int): Identifiant de l'utilisateur (clé primaire composée)
        item_id (int): Identifiant de l'article (clé primaire composée)
        acquired_at (datetime): Date et heure de l'achat

    Relationships:
        user (User): L'utilisateur qui a acheté l'article
        item (ShopItem): L'article qui a été acheté

    Note:
        La clé primaire est composée de (user_id, item_id), ce qui signifie
        qu'un utilisateur ne peut acheter un même article qu'une seule fois.
    """
    __tablename__ = "user_inventory"

    def __init__(self, **kwargs) -> None:
        """
        Initialise une nouvelle instance de liaison utilisateur-article.

        Args:
            **kwargs: Arguments nommés correspondant aux attributs du modèle
        """
        super().__init__(**kwargs)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), autoincrement=True, primary_key=True, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("shop_items.id"), primary_key=True, nullable=False)
    acquired_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    # Relations
    user = db.relationship("User", back_populates="inventory")
    item = db.relationship("ShopItem", back_populates="users")

    def to_dict(self):
        """
        Convertit la liaison utilisateur-article en dictionnaire.

        Returns:
            dict: Dictionnaire contenant les informations de l'article acheté
                - item_id (int): Identifiant de l'article
                - acquired_at (datetime): Date d'achat
        """
        return {
            "item_id": self.item_id,
            "acquired_at": self.acquired_at
        }
