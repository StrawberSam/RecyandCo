"""
Utilitaires réutilisables pour les services.

Ce module contient des fonctions helper pour éviter la répétition de code
dans les services (principe DRY). Ces fonctions centralisent les validations
et récupérations d'entités courantes.
"""

from typing import Any, Dict, Optional, Tuple

from db.models import User


def validate_user_id(user_id) -> Optional[Dict[str, Any]]:
    """
    Valide que user_id est un entier.
    Cette fonction centralise la validation du type de user_id pour éviter
    de répéter ce contrôle dans tous les services.

    Args:
        user_id: Valeur à valider (devrait être un int)

    Returns:
        dict ou None:
            - None si user_id est un entier valide
            - dict d'erreur si user_id n'est pas un entier
    """

    if not isinstance(user_id, int):
        return {
            "success": False,
            "message": "user_id doit être un entier",
            "status_code": 400
        }
    return None

def get_user_or_404(db, user_id: int) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
    """
    Récupère un utilisateur depuis la base de données ou retourne une erreur 404.
    Cette fonction centralise la récupération d'utilisateur avec gestion d'erreur
    automatique. Elle utilise le pattern Result (valeur, erreur).

    Args:
        db: Instance SQLAlchemy (self.db depuis un service)
        user_id (int): Identifiant de l'utilisateur à récupérer

    Returns:
        tuple: (utilisateur, erreur)
            - Si succès : (User object, None)
            - Si échec : (None, dict d'erreur)

    Note:
        Cette fonction suppose que user_id a déjà été validé avec validate_user_id().
    """

    utilisateur = db.session.get(User, user_id)
    if not utilisateur:
        return None, {
            "success": False,
            "message": "Utilisateur introuvable",
            "status_code": 400
        }
    return utilisateur, None

def validate_and_get_user(db, user_id) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
    """
    Valide user_id ET récupère l'utilisateur en une seule fonction.
    Cette fonction combine validate_user_id() et get_user_or_404() pour
    simplifier encore plus le code des services.

    Args:
        db: Instance SQLAlchemy (self.db depuis un service)
        user_id: Identifiant à valider et utiliser pour récupérer l'utilisateur

    Returns:
        tuple: (utilisateur, erreur)
            - Si succès : (User object, None)
            - Si échec : (None, dict d'erreur avec le bon status_code)

    Note:
        Fonction tout-en-un, la plus pratique pour la majorité des cas.
    """

    # Validation du type
    error = validate_user_id(user_id)
    if error:
        return None, error

    # Récupère depuis la db
    utilisateur, error = get_user_or_404(db, user_id)
    if error:
        return None, error

    # Succès
    return utilisateur, None

def validate_limit(limit) -> Optional[Dict[str, Any]]:
    """
    Valide qu'une limite (pour pagination) est un entier.
    Utilisé notamment dans get_leaderboard() pour valider le paramètre limit.

    Args:
        limit: Valeur à valider (devrait être un int)

    Returns:
        dict ou None:
            - None si limit est un entier valide
            - dict d'erreur si limit n'est pas un entier
    """

    if not isinstance(limit, int):
        return {
            "success": False,
            "message": "Limit doit être un entier",
            "status_code": 400
        }
    return None
