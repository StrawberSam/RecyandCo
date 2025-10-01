import bcrypt

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
