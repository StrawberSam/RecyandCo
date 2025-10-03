from dotenv import load_dotenv
load_dotenv() # Charge le fichier .env

import os
from flask import Flask
from db import db
from config import config
from utils import security
from services.auth_service import AuthService
from facade.auth_facade import auth_bp
from facade.badge_facade import badge_bp
from services.badge_service import BadgeService

# Initialisation de l’app Flask
app = Flask(__name__)

# Récupération de la config (par défaut : development)
app_config = config["development"]()
app.config.from_object(app_config)

# Ajouter l'ID admin depuis le .env
app.config["ADMIN_ID"] = int(os.getenv("ADMIN_ID", 0))

# Initialisation de la DB avec Flask
db.init_app(app)

# Importer les modèles (important pour db.create_all())
from db import models
with app.app_context():
    db.create_all()

# Instanciation des services
auth_service = AuthService(db, security, app_config)
badge_service = BadgeService(db)

# Stockage des services dans app.config
app.config["services"] = {
    "auth": auth_service,
    "badge": badge_service,
}

# Routes
app.register_blueprint(auth_bp)
app.register_blueprint(badge_bp)


if __name__ == "__main__":
    app.run(debug=True)
