from db.models import ShopItem, User, UserInventory, db

class ShopService:
    def __init__(self, db):
        self.db = db

    def get_active_items(self):
        # requête pour récupérer les items
        resultat = (
            self.db.session.query(ShopItem)
            .with_entities(ShopItem.id, ShopItem.name, ShopItem.price)
            .order_by(ShopItem.price.asc())
            .filter_by(is_active=True)
            .all()
        )

        active_items = []
        for id, name, price in resultat:
            active_items.append({
                "id": id,
                "name": name,
                "price": price
            })

        return {
            "success": True,
            "data": active_items,
            "status_code": 200
        }

    def can_purchase(self, user_id, item_id):
        # Rechercher user
        utilisateur = self.db.session.get(User, user_id)
        if not utilisateur:
            return {"success": False, "message": "Utilisateur introuvable", "status_code": 404}

        # Vérification que article existe et est actif
        article = self.db.session.get(ShopItem, item_id)
        if not article:
            return {"success": False, "message": "Article introuvable", "status_code": 404}

        if not article.is_active:
            return {"success": False, "message": "Article indisponible", "status_code": 400}

        # Vérification si l'user n'a pas déjà l'article
        owned_item = self.db.session.get(UserInventory, (user_id, item_id))
        if owned_item:
            return {"success": False, "message": "Article déjà possédé", "status_code": 409}

        # Vérifier le solde de points
        if utilisateur.total_score < article.price:
            return {"success": False, "message": "Points insuffisants", "status_code": 403}

        #Return si tout ok
        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "item_id": item_id,
                "can_purchase": True,
                "price": article.price
            },
            "status_code": 200
        }

    def purchase_item(self, user_id, item_id):
        # Rechercher user
        utilisateur = self.db.session.get(User, user_id)
        if not utilisateur:
            return {"success": False, "message": "Utilisateur introuvable", "status_code": 404}

        # Vérification que article existe et est actif
        article = self.db.session.get(ShopItem, item_id)
        if not article:
            return {"success": False, "message": "Article introuvable", "status_code": 404}

        if not article.is_active:
            return {"success": False, "message": "Article indisponible", "status_code": 400}

        # Vérification si l'user n'a pas déjà l'article
        owned_item = self.db.session.get(UserInventory, (user_id, item_id))
        if owned_item:
            return {"success": False, "message": "Article déjà possédé", "status_code": 409}

        # Vérifier le solde de points
        if utilisateur.total_score < article.price:
            return {"success": False, "message": "Points insuffisants", "status_code": 403}

        # MaJ des données
        utilisateur.total_score -= article.price

        # Nouvelle donnée
        nouvelle_ligne = UserInventory(user_id=user_id, item_id=item_id)
        self.db.session.add(nouvelle_ligne)
        self.db.session.commit()

        return {
            "success": True,
            "message": "Article acheté avec succès",
            "data": {
                "user_id": user_id,
                "item_id": item_id,
                "new_total_score": utilisateur.total_score
            },
            "status_code": 200
        }
