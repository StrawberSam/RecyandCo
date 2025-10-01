from sqlalchemy.ext.declarative import declarative_base # Import pour déclarer les classes
from sqlalchemy import Boolean, Text, Column, ForeignKey, String, DateTime, CHAR, Integer # Import pour définir les colonnes
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base() # La classe de base de tous nos modèles

# ---------- USER ----------
class User(Base):
    __tablename__ = "users" # Nom de la table dans MySQL

    # Création des colonnes qui doivent correspondre à la table SQL
    id = Column(CHAR(36), primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    #Relations
    scores = relationship("Score", back_populates="user")
    badges = relationship("UserBadge", back_populates="user")
    inventory = relationship("UserInventory", back_populates="user")

    def to_dict(self):
        # Retourne un utilisateur sous forme de dictionnaire pour API
        return{
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "last_login_at": self.last_login_at
        }

    def to_public_dict(self):
        # Retourne un utilisateur sous forme de dictionnaire public
        return{
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at,
            "last_login_at": self.last_login_at
        }

# ---------- SCORE ----------
class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    points = Column(Integer, nullable=False)
    correct_items = Column(Integer, nullable=False)
    total_items = Column(Integer, nullable=False)
    duration_ms = Column(Integer, nullable=False)
    played_at = Column(DateTime, server_default=func.now(), nullable=False)

    #Relations
    user = relationship("User", back_populates="scores")

    def efficiency(self):
        # Calcule le ratio correct_item/total_item
        if self.total_items == 0:
            return 0
        return self.correct_items / self.total_items

    def to_dict(self):
        return{
            "id": self.id,
            "points": self.points,
            "correct_items": self.correct_items,
            "total_items": self.total_items,
            "duration_ms": self.duration_ms,
            "played_at": self.played_at,
            "efficiency": self.efficiency()
        }

# ---------- BADGE ----------
class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, autoincrement=True, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    label = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    threshold = Column(Integer, nullable=True)
    icon = Column(String(255), nullable=True)

    # Relations
    users = relationship("UserBadge", back_populates="badge")

    def to_dict(self):
        return{
            "id": self.id,
            "code": self.code,
            "label": self.label,
            "description": self.description,
            "threshold": self.threshold,
            "icon": self.icon
        }

# ---------- USERBADGE ----------
class UserBadge(Base):
    __tablename__ = "user_badges"

    user_id = Column(CHAR(36), ForeignKey("users.id"), primary_key=True, nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id"), primary_key=True, nullable=False)
    awarded_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relations
    user = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="users")

    def to_dict(self):
        return{
            "badge_id": self.badge_id,
            "awarded_at": self.awarded_at
        }

# ---------- SHOPITEM ----------
class ShopItem(Base):
    __tablename__ = "shop_items"

    id = Column(Integer, autoincrement=True, primary_key=True)
    sku = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default="1")

    # Relations
    users = relationship("UserInventory", back_populates="item")

    def to_dict(self):
        return{
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "price": self.price,
            "is_active": self.is_active
        }

# ---------- USERINVENTORY ----------
class UserInventory(Base):
    __tablename__ = "user_inventory"

    user_id = Column(CHAR(36), ForeignKey("users.id"), primary_key=True, nullable=False)
    item_id = Column(Integer, ForeignKey("shop_items.id"), primary_key=True, nullable=False)
    acquired_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relations
    user = relationship("User", back_populates="inventory")
    item = relationship("ShopItem", back_populates="users")

    def to_dict(self):
        return{
            "item_id": self.item_id,
            "acquired_at": self.acquired_at
        }
