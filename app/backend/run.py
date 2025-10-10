from dotenv import load_dotenv
load_dotenv() # Charge le fichier .env

import os
from flask import Flask
from flask_migrate import Migrate
from db import db
from config import config
from utils import security
from services.auth_service import AuthService
from services.badge_service import BadgeService
from services.score_service import ScoreService
from services.shop_service import ShopService
from facade.auth_facade import auth_bp
from facade.badge_facade import badge_bp
from facade.score_facade import score_bp
from facade.shop_facade import shop_bp
from facade.rules_facade import rules_bp

# Initialisation de l’app Flask
app = Flask(__name__)

# Récupération de la config (par défaut : development)
app_config = config["development"]()
app.config.from_object(app_config)

# Ajouter l'ID admin depuis le .env
app.config["ADMIN_ID"] = int(os.getenv("ADMIN_ID", 0))

# Initialisation de la DB avec Flask
db.init_app(app)
# Gestion des migrations
migrate = Migrate(app, db)

# Instanciation des services
auth_service = AuthService(db, security, app_config)
badge_service = BadgeService(db)
score_service = ScoreService(db)
shop_service = ShopService(db)

# Stockage des services dans app.config
app.config["services"] = {
    "auth": auth_service,
    "badge": badge_service,
    "score": score_service,
    "shop": shop_service
}

# Routes
app.register_blueprint(auth_bp)
app.register_blueprint(badge_bp)
app.register_blueprint(score_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(rules_bp)


if __name__ == "__main__":
    app.run(debug=True)
