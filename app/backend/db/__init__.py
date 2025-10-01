from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config

# Charger la configuration (défaut = dev)
db_config = config["development"]()

# Crée le moteur SQLAlchemy avec l’URL de la DB depuis .env
engine = create_engine(db_config.SQLALCHEMY_DATABASE_URI, echo=True)

# Fabrique de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Instancie une session utilisable dans tes services
db_session = SessionLocal()
