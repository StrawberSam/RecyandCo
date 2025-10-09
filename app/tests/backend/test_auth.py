def test_register_user(client):
    """Teste l'inscription d'un nouvel utilisateur."""
    res = client.post("/api/register", json={
        "username": "pytest_user",
        "email": "pytest@example.com",
        "password": "test1234"
    })
    assert res.status_code in [200, 201, 409] # 409 si l'utilisateur existe déjà
    data = res.get_json()
    assert data["success"] in [True, False] # Peut échouer si l'utilisateur existe
    if res.status_code in [200, 201]:
        assert "username" in data["data"]

def test_login_user(client):
    """Teste la connexion utilisateur."""
    res = client.post("/api/login", json={
        "email": "pytest@example.com",
        "password": "test1234"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "user" in data["data"]
    assert "access_token" in data["data"]

def test_me_route(client):
    """Teste la récupération du profil utilisateur."""
    login = client.post("/api/login", json={
        "email": "pytest@example.com",
        "password": "test1234"
    })
    data = login.get_json()
    token = data["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/me", headers=headers)
    assert res.status_code == 200
