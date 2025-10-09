import sys
from pathlib import Path
import pytest

# Ajoute le dossier backend au PYTHONPATH
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from run import app, db

@pytest.fixture(scope="session")
def client():
    app.config.update({"TESTING": True})
    with app.app_context():
        db.create_all()
    with app.test_client() as client:
        yield client
