def test_get_badges(client):
    """Vérifie que la route /api/badges/me fonctionne."""
    login = client.post("/api/login", json={
        "email": "pytest@example.com",
        "password": "test1234"
    })
    data = login.get_json()
    token = data["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/badges/me", headers=headers)
    assert res.status_code == 200
