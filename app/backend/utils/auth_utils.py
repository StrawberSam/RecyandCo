from typing import Any, Dict, Optional, Tuple

from flask import current_app, request


def verify_token_and_get_user_id() -> Tuple[Optional[int], Optional[Dict[str, Any]]] :
    """
    Vérifie le token JWT depuis les cookies et retourne l'ID utilisateur.

    Cette fonction centralise toute la logique de vérification du token :
    1. Récupère le token d'accès depuis les cookies de la requête
    2. Vérifie que le token est présent
    3. Valide le token via le service d'authentification
    4. Extrait et retourne l'user_id

    Returns:
        tuple: (user_id, error_response)
            - Si succès : (user_id: int, None)
                Exemple : (42, None)
            - Si échec : (None, error_response: dict)
                Exemple : (None, {"success": False, "message": "Token manquant", "status_code": 401})

    Note:
        Cette fonction utilise le service d'authentification configuré dans
        current_app.config["services"]["auth"]
    """

    # Récupérer le service depuis config Flask
    auth_service = current_app.config["services"]["auth"]

    # Récupérer token depuis les cookies
    token = request.cookies.get("access_token")

    # Vérif si token présent
    if not token:
        return None, {
            "success": False,
            "message": "Token manquant",
            "status_code": 401
        }

    # Validation token via service d'authentification
    user_response = auth_service.get_user_by_id(token)

    # Vérif si token valide
    if not user_response.get("success"):
        return None, {
            "success": False,
            "message": user_response.get("message", "Token invalide"),
            "status_code": 401
        }

    # Extraire user_id depuis la réponse du service
    user_id = user_response["data"]["id"]

    # Retourner user_id
    return user_id, None

def set_auth_cookies(response, access_token: str, refresh_token: Optional[str] = None):
    """
    Configure les cookies d'authentification sur une réponse Flask.

    Cette fonction centralise la configuration des cookies JWT pour garantir
    une configuration cohérente à travers toute l'application (login, refresh).

    Args:
        response: Objet Response de Flask (créé avec make_response)
        access_token (str): Token d'accès JWT (courte durée : 1 heure)
        refresh_token (str | None, optional): Token de rafraîchissement JWT (longue durée : 7 jours)
            Si None, seul l'access_token est configuré

    Returns:
        Response: L'objet response modifié (permet le chaînage)

    Note:
        Configuration des cookies :
        - httponly=True : Protection XSS (pas accessible via JavaScript)
        - secure=False : À mettre True en production avec HTTPS
        - samesite="Lax" : Protection CSRF partielle
        - max_age : Durée de vie en secondes
    """

    # Config cookie access_token
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=60*60 # 1 heure
    )

    # Config refresh_token
    if refresh_token:
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=60*60*24*7 # 7 jours
        )

    return response

def clear_auth_cookies(response):
    """
    Supprime les cookies d'authentification (utilisé lors de la déconnexion).

    Cette fonction supprime les cookies en les remplaçant par des cookies vides
    avec max_age=0, ce qui force le navigateur à les supprimer immédiatement.

    Args:
        response: Objet Response de Flask (créé avec make_response)

    Returns:
        Response: L'objet response modifié (permet le chaînage)

    Note:
        Important : Les paramètres (httponly, secure, samesite, path) doivent être
        IDENTIQUES à ceux utilisés lors de la création des cookies, sinon la
        suppression peut échouer dans certains navigateurs.
    """

    # Supprimer le cookie access_token
    response.set_cookie(
        'access_token',
        value='',
        max_age=0,
        httponly=True,
        secure=False,
        samesite='Lax',
        path='/'
    )

    # Supprimer le cookie refresh_token
    response.set_cookie(
        'refresh_token',
        value='',
        max_age=0,
        httponly=True,
        secure=False,
        samesite='Lax',
        path='/'
    )

    return response
