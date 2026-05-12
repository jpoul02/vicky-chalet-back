import pytest
from app.core.security import hash_password
from app.models.usuario import Usuario


def _create_user(db, email="test@test.com", password="secret123"):
    user = Usuario(
        email=email,
        hashed_password=hash_password(password),
        negocio_nombre="Test Negocio",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestLogin:
    def test_login_success(self, client, db):
        _create_user(db)
        r = client.post("/v1/auth/login", json={"email": "test@test.com", "password": "secret123"})
        assert r.status_code == 200
        assert "access_token" in r.cookies

    def test_login_wrong_password(self, client, db):
        _create_user(db)
        r = client.post("/v1/auth/login", json={"email": "test@test.com", "password": "wrong"})
        assert r.status_code == 401

    def test_login_unknown_email(self, client, db):
        r = client.post("/v1/auth/login", json={"email": "nobody@test.com", "password": "x"})
        assert r.status_code == 401


class TestMe:
    def test_me_authenticated(self, client, db):
        _create_user(db)
        client.post("/v1/auth/login", json={"email": "test@test.com", "password": "secret123"})
        r = client.get("/v1/auth/me")
        assert r.status_code == 200
        assert r.json()["email"] == "test@test.com"

    def test_me_unauthenticated(self, client):
        r = client.get("/v1/auth/me")
        assert r.status_code == 401


class TestLogout:
    def test_logout_clears_cookie(self, client, db):
        _create_user(db)
        client.post("/v1/auth/login", json={"email": "test@test.com", "password": "secret123"})
        r = client.post("/v1/auth/logout")
        assert r.status_code == 200
