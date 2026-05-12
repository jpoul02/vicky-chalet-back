import pytest
from app.core.security import hash_password, create_access_token
from app.models.usuario import Usuario
from app.models.periodo import Periodo
from app.models.costo_fijo import CostoFijo


def _auth(client, db):
    user = Usuario(email="u@t.com", hashed_password=hash_password("pw"), negocio_nombre="N")
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    client.cookies.set("access_token", token)
    return user


def _periodo(db, usuario_id, año=2026, mes=5, estado="activo"):
    p = Periodo(usuario_id=usuario_id, año=año, mes=mes, estado=estado)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


class TestGetPeriodos:
    def test_lista_periodos(self, client, db):
        user = _auth(client, db)
        _periodo(db, user.id)
        r = client.get("/v1/periodos")
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_requiere_auth(self, client):
        r = client.get("/v1/periodos")
        assert r.status_code == 401


class TestGetActivo:
    def test_retorna_periodo_activo(self, client, db):
        user = _auth(client, db)
        _periodo(db, user.id, estado="activo")
        r = client.get("/v1/periodos/activo")
        assert r.status_code == 200
        assert r.json()["estado"] == "activo"

    def test_retorna_404_si_no_hay_activo(self, client, db):
        _auth(client, db)
        r = client.get("/v1/periodos/activo")
        assert r.status_code == 404


class TestCrearPeriodo:
    def test_crear_periodo(self, client, db):
        _auth(client, db)
        r = client.post("/v1/periodos", json={"año": 2026, "mes": 6})
        assert r.status_code == 201
        assert r.json()["mes"] == 6
        assert r.json()["estado"] == "activo"

    def test_no_dos_activos(self, client, db):
        user = _auth(client, db)
        _periodo(db, user.id, estado="activo")
        r = client.post("/v1/periodos", json={"año": 2026, "mes": 7})
        assert r.status_code == 409


class TestCerrarPeriodo:
    def test_cierre_calcula_ganancia(self, client, db):
        user = _auth(client, db)
        p = _periodo(db, user.id, estado="activo")
        cf = CostoFijo(nombre="Alquiler", monto=400.0, tipo="alquiler", activo=True)
        db.add(cf)
        db.commit()
        r = client.patch(
            f"/v1/periodos/{p.id}/cerrar",
            json={"resultado_neto": 2000.0, "ahorro": 300.0},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["ganancia_real"] == 2000.0 - body["total_egresos"]
        assert body["ahorro"] == 300.0
