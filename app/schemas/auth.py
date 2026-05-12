from pydantic import BaseModel


class LoginInput(BaseModel):
    email: str
    password: str


class PinLoginInput(BaseModel):
    pin: str


class UsuarioOut(BaseModel):
    id: str
    email: str
    negocio_nombre: str

    model_config = {"from_attributes": True}


class LoginOut(BaseModel):
    id: str
    email: str
    negocio_nombre: str
    access_token: str
