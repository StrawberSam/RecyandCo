import re

def is_valid_email(email: str) -> bool:
    # Regex stricte : uniquement lettres anglaises, chiffres, . et -
    pattern = r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

def is_valid_password(password: str) -> bool:
    return len(password) >= 8
