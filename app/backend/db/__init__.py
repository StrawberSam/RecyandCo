from flask_sqlalchemy import SQLAlchemy

# On instancie un objet global db
# qui sera importé dans models.py et initialisé dans app.py
db = SQLAlchemy()
