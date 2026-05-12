from app.core.security import hash_password, create_access_token
from app.models.usuario import Usuario
from app.models.costo_fijo import CostoFijo


def _auth(client, db):
    user = Usuario(email="u@t.com", hashed_password=hash_password("pw"), negocio_nombre="N")
    db.add(user)
    db.commit()
    db.refresh(user)
    client.cookies.set("access_token", create_access_token(user.id))
    return user


class TestCostosFijos:
    def test_list_empty(self, client, db):
        _auth(client, db)
        r = client.get("/v1/costos-fijos")
        assert r.status_code == 200
        assert r.json() == []

    def test_create(self, client, db):
        _auth(client, db)
        r = client.post("/v1/costos-fijos", json={"nombre": "Alquiler", "monto": 400.0, "tipo": "alquiler"})
        assert r.status_code == 201
        assert r.json()["activo"] is True

    def test_update_activo(self, client, db):
        _auth(client, db)
        cf = CostoFijo(nombre="Salario", monto=300.0, tipo="salario", activo=True)
        db.add(cf)
        db.commit()
        db.refresh(cf)
        r = client.put(f"/v1/costos-fijos/{cf.id}", json={"activo": False})
        assert r.status_code == 200
        assert r.json()["activo"] is False

    def test_delete(self, client, db):
        _auth(client, db)
        cf = CostoFijo(nombre="Otro", monto=100.0, tipo="otro", activo=True)
        db.add(cf)
        db.commit()
        db.refresh(cf)
        r = client.delete(f"/v1/costos-fijos/{cf.id}")
        assert r.status_code == 204
