import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

def hash_password(password: str) -> str:
    """
    Hache un mot de passe en clair avec bcrypt de manière sécurisée.

    Args:
        password (str): mot de passe en clair fourni par l’utilisateur.

    Returns:
        str: le mot de passe haché (sous forme de chaîne de caractères).
    """

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Vérifie si un mot de passe correspond à son hash stocké.

    Args:
        password (str): mot de passe en clair fourni par l’utilisateur.
        hashed_password (str): hash du mot de passe stocké en base de données.

    Returns:
        bool: True si le mot de passe est correct, False sinon.
    """

    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_token(data: dict, secret: str, expiration_minutes: int = 60) -> str:
    """
    Crée un JWT signé pour un utilisateur.

    Args:
        data (dict): Données à inclure dans le token (id, username).
        secret (str): Clé secrète pour signer le token.
        expiration_minutes (int): Durée de validité du token en minutes (par défaut 60).

    Returns:
        str: Le token JWT encodé.
    """
    
    payload = {
        **data,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expiration_minutes)
    }

    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

