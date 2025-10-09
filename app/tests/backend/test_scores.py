def test_add_score(client):
    """Ajout d'un score après une partie."""
    login = client.post("/api/login", json={
        "email": "pytest@example.com",
        "password": "test1234"
    })
    data = login.get_json()
    token = data["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/scores", json={
        "points": 10,
        "correct_items": 8,
        "total_items": 10,
        "duration_ms": 5000
    }, headers=headers)

    # debug
    if res.status_code == 400:
        print(f"\n erreur 400: {res.get_json()}")
    assert res.status_code in [200, 201]

def test_get_scores(client):
    """Vérifie que la liste des scores utilisateur est accessible."""
    login = client.post("/api/login", json={
        "email": "pytest@example.com",
        "password": "test1234"
    })
    data = login.get_json()
    token = data["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/scores/me", headers=headers)
    assert res.status_code == 200
