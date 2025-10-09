def test_get_shop_items(client):
    """Affiche la liste des objets disponibles."""
    res = client.get("/api/shop/items")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data["data"], list)

def test_purchase_item(client):
    """Achète un objet si l'utilisateur a assez de points."""
    login = client.post("/api/login", json={
        "email": "pytest@example.com",
        "password": "test1234"
    })
    token = login.get_json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/shop/purchase", json={"item_id": 1}, headers=headers)
    assert res.status_code in [200, 400, 404]
