import pytest

def test_register(client):
    resp = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_register_duplicate_username(client):
    client.post("/api/auth/register", json={
        "username": "dupuser",
        "email": "dup1@example.com",
        "password": "password123",
    })
    resp = client.post("/api/auth/register", json={
        "username": "dupuser",
        "email": "dup2@example.com",
        "password": "password123",
    })
    assert resp.status_code == 400

def test_login(client):
    client.post("/api/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "password123",
    })
    resp = client.post("/api/auth/token", data={
        "username": "loginuser",
        "password": "password123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "username": "wrongpass",
        "email": "wrongpass@example.com",
        "password": "correct",
    })
    resp = client.post("/api/auth/token", data={
        "username": "wrongpass",
        "password": "wrong",
    })
    assert resp.status_code == 401

def test_me(client):
    client.post("/api/auth/register", json={
        "username": "meuser",
        "email": "me@example.com",
        "password": "password123",
    })
    token_resp = client.post("/api/auth/token", data={
        "username": "meuser",
        "password": "password123",
    })
    token = token_resp.json()["access_token"]
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "meuser"
