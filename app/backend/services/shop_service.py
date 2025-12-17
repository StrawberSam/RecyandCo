"""
Service de gestion de la boutique virtuelle pour Récy&Co.

Ce module gère toute la logique de la boutique :
affichage des articles disponibles, vérification des conditions d'achat,
et traitement des achats avec déduction des points.

Classes:
    ShopService: Service principal pour la gestion de la boutique
"""

from db.models import ShopItem, User, UserInventory
from utils.services_utils import validate_and_get_user

class ShopService:
    """
    Service gérant la boutique virtuelle et les achats d'articles.

    Ce service encapsule toute la logique de la boutique :
    - Récupération des articles disponibles à l'achat
    - Vérification des conditions d'achat (points suffisants, article non possédé)
    - Traitement des achats (déduction des points, ajout à l'inventaire)

    Le système d'achat utilise les points accumulés dans le jeu comme monnaie.
    Chaque article ne peut être acheté qu'une seule fois par utilisateur.

    Attributes:
        db: Instance de SQLAlchemy pour les opérations de base de données
    """
    def __init__(self, db):
        """
        Initialise le service de gestion de la boutique.

        Args:
            db: Instance SQLAlchemy pour les accès à la base de données
        """
        self.db = db

    def _validate_purchase_conditions(self, user_id, item_id):
        """
        Valide toutes les conditions nécessaires pour un achat.
        Cette méthode privée centralise toutes les vérifications communes
        entre can_purchase() et purchase_item().

        Args:
            user_id (int): Identifiant de l'utilisateur
            item_id (int): Identifiant de l'article

        Returns:
            tuple: (utilisateur, article, erreur)
                - Si succès : (User object, ShopItem object, None)
                - Si échec : (None, None, dict d'erreur)

        Note:
            Méthode privée (préfixe _) utilisée uniquement en interne par la classe.
        """

        # Validation et récupération de l'utilisateur
        utilisateur, error = validate_and_get_user(self.db, user_id)
        if error:
            return None, None, error

        assert utilisateur is not None, "utilisateur ne peut pas être None ici"

        # Vérification si article existant
        article = self.db.session.get(ShopItem, item_id)
        if not article:
            return None, None, {
                "success": False,
                "message": "Article introuvable",
                "status_code": 404
                }

        # Vérification si article actif
        if not article.is_active:
            return None, None, {
                "success": False,
                "message": "Article indisponible",
                "status_code": 400
                }

        # Vérification si l'utilisateur ne possède pas déjà l'article
        owned_item = self.db.session.get(UserInventory, (user_id, item_id))
        if owned_item:
            return None, None, {
                "success": False,
                "message": "Article déjà possédé",
                "status_code": 409
                }

        # Vérifier le solde de points
        if utilisateur.total_score < article.price:
            return None, None, {
                "success": False,
                "message": "Points insuffisants",
                "status_code": 403
                }

        return utilisateur, article, None

    def get_active_items(self):
        """
        Récupère la liste des articles actifs disponibles à l'achat.

        Cette méthode retourne uniquement les articles actifs (is_active=True),
        triés par prix croissant pour faciliter la navigation.

        Returns:
            dict: Dictionnaire contenant :
                - success (bool): Toujours True
                - data (list): Liste de dictionnaires triés par prix, chacun contenant :
                    - id (int): Identifiant de l'article
                    - name (str): Nom de l'article
                    - price (int): Prix en points
                - status_code (int): 200 (succès)

        Note:
            Les articles désactivés (is_active=False) n'apparaissent pas
            dans cette liste mais restent en base de données.
        """
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
        """
        Vérifie si un utilisateur peut acheter un article spécifique.

        Args:
            user_id (int): Identifiant de l'utilisateur
            item_id (int): Identifiant de l'article à acheter

        Returns:
            dict: Dictionnaire contenant :
                - success (bool): True si l'achat est possible, False sinon
                - data (dict): Si succès, contient :
                    - user_id (int): Identifiant de l'utilisateur
                    - item_id (int): Identifiant de l'article
                    - can_purchase (bool): Toujours True si succès
                    - price (int): Prix de l'article
                  OU
                - message (str): Message d'erreur expliquant pourquoi l'achat est impossible
                - status_code (int): Code HTTP approprié
                    - 200 : Achat possible
                    - 400 : Article indisponible
                    - 403 : Points insuffisants
                    - 404 : Utilisateur ou article introuvable
                    - 409 : Article déjà possédé

        Note:
            Cette méthode ne modifie pas la base de données, elle ne fait
            que vérifier les conditions. Pour effectuer l'achat, utilisez
            purchase_item().
        """

        # Validation conditions d'achat
        _, article, error = self._validate_purchase_conditions(user_id, item_id)
        if error:
            return error

        assert article is not None

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
        """
        Effectue l'achat d'un article pour un utilisateur.

        Cette méthode traite l'achat complet d'un article :
        1. Vérifie toutes les conditions d'achat (même vérifications que can_purchase)
        2. Déduit le prix de l'article du score total de l'utilisateur
        3. Ajoute l'article à l'inventaire de l'utilisateur
        4. Commit les changements en base de données

        Args:
            user_id (int): Identifiant de l'utilisateur
            item_id (int): Identifiant de l'article à acheter

        Returns:
            dict: Dictionnaire contenant :
                - success (bool): True si l'achat a réussi
                - message (str): Message de confirmation
                - data (dict): Informations sur l'achat :
                    - user_id (int): Identifiant de l'utilisateur
                    - item_id (int): Identifiant de l'article acheté
                    - new_total_score (int): Nouveau score total après déduction
                  OU
                - message (str): Message d'erreur si échec
                - status_code (int): Code HTTP approprié
                    - 200 : Achat réussi
                    - 400 : Article indisponible
                    - 403 : Points insuffisants
                    - 404 : Utilisateur ou article introuvable
                    - 409 : Article déjà possédé

        Note:
            Cette méthode effectue une transaction complète (déduction + ajout).
            Si l'utilisateur ferme sa page entre la vérification et l'achat,
            les conditions seront revérifiées.

        Warning:
            Les vérifications sont dupliquées entre can_purchase() et purchase_item()
            pour éviter les conditions de course (race conditions). Un utilisateur
            malveillant ne peut pas acheter un article en spammant des requêtes.
        """
        # Validation des conditions d'achat
        utilisateur, article, error = self._validate_purchase_conditions(user_id, item_id)
        if error:
            return error

        assert utilisateur is not None
        assert article is not None

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
