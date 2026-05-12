from datetime import date
from app.core.security import hash_password, create_access_token
from app.models.usuario import Usuario
from app.models.periodo import Periodo
from app.models.inversion import Inversion


def _auth(client, db):
    user = Usuario(email="u@t.com", hashed_password=hash_password("pw"), negocio_nombre="N")
    db.add(user)
    db.commit()
    db.refresh(user)
    client.cookies.set("access_token", create_access_token(user.id))
    return user


def _periodo(db, uid):
    p = Periodo(usuario_id=uid, año=2026, mes=5, estado="activo")
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _inversion(db, periodo_id):
    inv = Inversion(
        periodo_id=periodo_id,
        descripcion="pan",
        monto=50.0,
        fecha=date.today(),
        tipo="adicional",
        origen="webapp",
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


class TestGetInversiones:
    def test_lista_inversiones_del_periodo(self, client, db):
        user = _auth(client, db)
        p = _periodo(db, user.id)
        _inversion(db, p.id)
        r = client.get(f"/v1/periodos/{p.id}/inversiones")
        assert r.status_code == 200
        assert len(r.json()) == 1


class TestCreateInversion:
    def test_crear_inversion(self, client, db):
        user = _auth(client, db)
        p = _periodo(db, user.id)
        r = client.post(
            f"/v1/periodos/{p.id}/inversiones",
            json={"descripcion": "insumos", "monto": 120.0, "tipo": "adicional"},
        )
        assert r.status_code == 201
        assert r.json()["monto"] == 120.0
        assert r.json()["origen"] == "webapp"

    def test_crear_whatsapp_origin(self, client, db):
        user = _auth(client, db)
        p = _periodo(db, user.id)
        r = client.post(
            f"/v1/periodos/{p.id}/inversiones",
            json={"descripcion": "pan", "monto": 50.0, "tipo": "adicional", "origen": "whatsapp"},
        )
        assert r.json()["origen"] == "whatsapp"


class TestUpdateInversion:
    def test_actualizar_monto(self, client, db):
        user = _auth(client, db)
        p = _periodo(db, user.id)
        inv = _inversion(db, p.id)
        r = client.put(f"/v1/inversiones/{inv.id}", json={"monto": 75.0})
        assert r.status_code == 200
        assert r.json()["monto"] == 75.0


class TestDeleteInversion:
    def test_eliminar_inversion(self, client, db):
        user = _auth(client, db)
        p = _periodo(db, user.id)
        inv = _inversion(db, p.id)
        r = client.delete(f"/v1/inversiones/{inv.id}")
        assert r.status_code == 204
