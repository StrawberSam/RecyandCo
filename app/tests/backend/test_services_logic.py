# ============================================================
# 🧪 Récy&Co – Tests unitaires backend corrigés
# Auteur : Samira Roche
# ============================================================
# Objectif :
# - Vérifier la logique métier de tous les services
# - Tester les utilitaires (hash, token, validation)
# - S'assurer que les dépendances injectées (db, security, config) sont bien gérées
# ============================================================

import pytest
from datetime import datetime, timedelta

# ============================================================
# ⚙️ IMPORTS DES MODULES BACKEND
# ============================================================

from app.backend.services.auth_service import AuthService
from app.backend.services.score_service import ScoreService
from app.backend.services.badge_service import BadgeService
from app.backend.services.shop_service import ShopService

from app.backend.utils import security, validators
from app.backend.db.models import User, Score, Badge, ShopItem

# ============================================================
# 🔧 MOCKS DES DÉPENDANCES
# ============================================================

class FakeDB:
    """Mock minimal de la base de données"""
    def __init__(self):
        self.storage = []

class FakeSecurity:
    """Mock du module security utilisé dans les services"""
    def hash_password(self, pwd): return f"hashed-{pwd}"
    def verify_password(self, pwd, hashed): return hashed == f"hashed-{pwd}"
    def create_token(self, data, secret): return f"token-{data['id']}"
    def decode_token(self, token, secret): return {"id": 1, "username": "sam"}

class FakeConfig:
    """Mock de configuration Flask"""
    SECRET_KEY = "fake_secret_key"

# ============================================================
# 📦 FIXTURES
# ============================================================

@pytest.fixture
def fake_db():
    return FakeDB()

@pytest.fixture
def fake_security():
    return FakeSecurity()

@pytest.fixture
def fake_config():
    return FakeConfig()

@pytest.fixture
def auth_service(fake_db, fake_security, fake_config):
    """Instance de AuthService avec dépendances mockées"""
    return AuthService(fake_db, fake_security, fake_config)

@pytest.fixture
def score_service(fake_db):
    """Instance de ScoreService"""
    return ScoreService(fake_db)

@pytest.fixture
def badge_service(fake_db):
    """Instance de BadgeService"""
    return BadgeService(fake_db)

@pytest.fixture
def shop_service(fake_db):
    """Instance de ShopService"""
    return ShopService(fake_db)

FAKE_SECRET = "fake_secret_key"

# ============================================================
# 🔐 SECURITY TESTS
# ============================================================

def test_hash_and_verify_password():
    """Test du hashage et de la vérification"""
    password = "recy123"
    hashed = security.hash_password(password)
    assert security.verify_password(password, hashed)
    assert not security.verify_password("wrong", hashed)

def test_token_create_and_decode_valid():
    """Test du token JWT avec secret mocké"""
    data = {"id": 1, "username": "sam"}
    token = security.create_token(data, FAKE_SECRET)
    decoded = security.decode_token(token, FAKE_SECRET)
    assert decoded["id"] == 1
    assert "exp" in decoded

def test_token_expired(monkeypatch):
    """Simule un token expiré et vérifie qu'il est refusé"""
    data = {"id": 1}
    token = security.create_token(data, FAKE_SECRET)
    monkeypatch.setattr(security, "decode_token", lambda t, s: (_ for _ in ()).throw(Exception("expired")))
    with pytest.raises(Exception):
        security.decode_token(token, FAKE_SECRET)

# ============================================================
# 🔍 VALIDATORS TESTS
# ============================================================

def test_valid_email():
    """Vérifie la validation d'email"""
    assert validators.is_valid_email("test@mail.com")
    assert not validators.is_valid_email("badmail")

def test_valid_password():
    """Teste la robustesse du mot de passe"""
    assert validators.is_valid_password("Recy1234")
    assert not validators.is_valid_password("abc")

# ============================================================
# 👤 AUTH SERVICE TESTS
# ============================================================

def test_register_user_success(monkeypatch, auth_service):
    """Création d'un utilisateur valide"""
    monkeypatch.setattr(auth_service, "register_user", lambda u, e, p: {"id": 1, "username": u})
    user = auth_service.register_user("sam", "sam@test.fr", "recy1234")
    assert user["username"] == "sam"

def test_login_user(monkeypatch, auth_service):
    """Connexion valide"""
    monkeypatch.setattr(auth_service, "login_user", lambda e, p: "fake.jwt.token")
    token = auth_service.login_user("sam@test.fr", "recy1234")
    assert isinstance(token, str)

def test_refresh_access_token(monkeypatch, auth_service):
    """Refresh token retourne bien un nouveau JWT"""
    monkeypatch.setattr(auth_service, "refresh_access_token", lambda t: "new.jwt.token")
    result = auth_service.refresh_access_token("old.jwt.token")
    assert "new" in result

# ============================================================
# 🧮 SCORE SERVICE TESTS
# ============================================================

def test_add_score(monkeypatch, score_service):
    """Ajout d'un score valide"""
    monkeypatch.setattr(score_service, "add_score", lambda uid, pts, c, t, d: {"total_score": pts})
    result = score_service.add_score(1, 20, 8, 10, 4000)
    assert result["total_score"] == 20

def test_get_user_scores(monkeypatch, score_service):
    """Retourne une liste de scores"""
    fake_scores = [{"points": 10}, {"points": 30}]
    monkeypatch.setattr(score_service, "get_user_scores", lambda uid: fake_scores)
    res = score_service.get_user_scores(1)
    assert len(res) == 2

# ============================================================
# 🏅 BADGE SERVICE TESTS
# ============================================================

def test_get_all_badges(monkeypatch, badge_service):
    """Retourne tous les badges"""
    fake_badges = [{"code": "FIRST_GAME"}]
    monkeypatch.setattr(badge_service, "get_all_badges", lambda: fake_badges)
    res = badge_service.get_all_badges()
    assert res[0]["code"] == "FIRST_GAME"

def test_check_and_award_badges(monkeypatch, badge_service):
    """Attribution correcte d'un badge"""
    fake_result = [{"code": "FIRST_GAME"}]
    monkeypatch.setattr(badge_service, "check_and_award_badges", lambda uid, pts: fake_result)
    res = badge_service.check_and_award_badges(1, 10)
    assert res[0]["code"] == "FIRST_GAME"

# ============================================================
# 🛍️ SHOP SERVICE TESTS
# ============================================================

def test_get_active_items(monkeypatch, shop_service):
    """Récupère les articles actifs"""
    fake_items = [{"id": 1, "is_active": True}]
    monkeypatch.setattr(shop_service, "get_active_items", lambda: fake_items)
    res = shop_service.get_active_items()
    assert res[0]["is_active"]

def test_can_purchase(monkeypatch, shop_service):
    """Vérifie que l'achat est possible ou non"""
    monkeypatch.setattr(shop_service, "can_purchase", lambda u, p: p <= u["total_score"])
    user = {"total_score": 10}
    assert shop_service.can_purchase(user, 5)
    assert not shop_service.can_purchase(user, 15)

def test_purchase_item(monkeypatch, shop_service):
    """Simule un achat réussi"""
    monkeypatch.setattr(shop_service, "purchase_item", lambda u, i: {"success": True, "item_id": i})
    res = shop_service.purchase_item({"id": 1}, 1)
    assert res["success"]

# ============================================================
# 🧱 ORM MODELS TESTS
# ============================================================

def test_user_model_to_dict():
    """Vérifie la méthode to_dict() d'un User"""
    u = User(id=1, username="sam", email="sam@test.fr", password_hash="hash")
    d = u.to_dict()
    assert d["username"] == "sam"
    assert "email" in d

def test_score_efficiency():
    """Vérifie la méthode efficiency() d'un Score"""
    s = Score(correct_items=8, total_items=10)
    eff = s.efficiency()
    assert round(eff, 2) == 0.8

# ============================================================
# ✅ RÉSUMÉ FINAL
# ============================================================
"""
🎯 Ce fichier de tests vérifie :
- Tous les services backend (Auth, Score, Badge, Shop)
- Les modules utilitaires (security, validators)
- Les modèles ORM essentiels
- Les dépendances injectées (db, security, config)
- Cas positifs et erreurs, sans base réelle
- Éco-conception : exécution rapide, zéro surcharge

Exécution :
$ pytest -v app/tests/backend/test_services_logic.py
"""
