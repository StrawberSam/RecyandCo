import os
# Module standard Python pour accéder aux variables d'environnement et aux chemins de fichiers

# On récupère le chemin absolu du dossier où se trouve ce fichier (utile si on stocke des fichiers locaux)
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Classe de configuration de base.
    Elle contient les réglages par défaut, communs à tous les environnements.
    """
    # Clé secrète utilisée par Flask pour sécuriser les sessions et les tokens JWT.
    # La valeur est lue dans la variable d'environnement SECRET_KEY,
    # sinon 'default_secret_key' est utilisée (mais ce n'est PAS recommandé en production).
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", "60"))

    # Mode debug désactivé par défaut (plus sûr pour la production).
    DEBUG = False

        # Important pour éviter un warning Flask-SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """
    Configuration spécifique pour l'environnement de développement.
    Hérite des réglages de la classe Config et active le mode debug.
    """
    # En mode dev, on active le debug pour voir les erreurs directement dans le navigateur.
    DEBUG = True

    # URI de connexion à la base de données, lue depuis la variable d'environnement DATABASE_URL.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    # Désactive le suivi des modifications d'objets par SQLAlchemy
    # (fonctionnalité lourde et rarement nécessaire → économie de ressources).
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# Dictionnaire permettant de choisir facilement une configuration
# selon l'environnement ("development", "production", etc.).
config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
