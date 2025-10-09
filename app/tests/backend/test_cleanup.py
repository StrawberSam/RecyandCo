import pytest
from run import app, db
from db.models import User, Score, Badge, ShopItem, UserBadge

@pytest.mark.order("last")
def test_cleanup_database():
    """Nettoie la base MySQL après les tests Pytest."""
    with app.app_context():
        user = User.query.filter_by(email="pytest@example.com").first()
        if user:
            # Supprime d'abord les entités liées
            Score.query.filter_by(user_id=user.id).delete()
            UserBadge.query.filter_by(user_id=user.id).delete()
            # Puis l'utilisateur
            db.session.delete(user)
            db.session.commit()
            print("✅ Utilisateur pytest supprimé")
