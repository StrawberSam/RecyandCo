from sqlalchemy.sql import func
from . import db

# ---------- USER ----------
class User(db.Model):
    __tablename__ = "users"

    def __init__(self, **kwargs) -> None:
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
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "last_login_at": self.last_login_at
        }

    def to_public_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at,
            "last_login_at": self.last_login_at
        }

# ---------- SCORE ----------
class Score(db.Model):
    __tablename__ = "scores"

    def __init__(self, **kwargs) -> None:
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
        return 0 if self.total_items == 0 else self.correct_items / self.total_items

    def to_dict(self):
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
    __tablename__ = "badges"

    def __init__(self, **kwargs) -> None:
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
    __tablename__ = "user_badges"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), autoincrement=True, primary_key=True, nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey("badges.id"), primary_key=True, nullable=False)
    awarded_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    # Relations
    user = db.relationship("User", back_populates="badges")
    badge = db.relationship("Badge", back_populates="users")

    def to_dict(self):
        return {
            "badge_id": self.badge_id,
            "awarded_at": self.awarded_at
        }

# ---------- SHOPITEM ----------
class ShopItem(db.Model):
    __tablename__ = "shop_items"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    sku = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, server_default="1")

    # Relations
    users = db.relationship("UserInventory", back_populates="item")

    def to_dict(self):
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "price": self.price,
            "is_active": self.is_active
        }

# ---------- USERINVENTORY ----------
class UserInventory(db.Model):
    __tablename__ = "user_inventory"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), autoincrement=True, primary_key=True, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("shop_items.id"), primary_key=True, nullable=False)
    acquired_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    # Relations
    user = db.relationship("User", back_populates="inventory")
    item = db.relationship("ShopItem", back_populates="users")

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "acquired_at": self.acquired_at
        }
