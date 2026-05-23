def test_health(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_register(client):
    resp = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "secret123",
            "full_name": "Test User",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["role"] == "user"


def test_register_duplicate_email(client):
    payload = {
        "email": "dup@example.com",
        "password": "secret123",
        "full_name": "Dup User",
    }
    client.post("/auth/register", json=payload)
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 400


def test_login_success(client):
    client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "mypass",
            "full_name": "Login User",
        },
    )
    resp = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "mypass"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={"email": "wp@example.com", "password": "correct", "full_name": "WP User"},
    )
    resp = client.post(
        "/auth/login",
        json={"email": "wp@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_get_me(client):
    reg = client.post(
        "/auth/register",
        json={"email": "me@example.com", "password": "pass123", "full_name": "Me User"},
    )
    token = reg.json()["access_token"]
    resp = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@example.com"


def test_get_me_no_token(client):
    resp = client.get("/users/me")
    assert resp.status_code == 403


def test_get_me_invalid_token(client):
    resp = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert resp.status_code == 401


def test_admin_endpoint_forbidden_for_user(client):
    reg = client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "pass123",
            "full_name": "Normal User",
        },
    )
    token = reg.json()["access_token"]
    resp = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
