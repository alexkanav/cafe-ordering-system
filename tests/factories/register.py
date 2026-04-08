from domain import schemas

name = "admin"
email = "admin@test.com"
password = "1234"


def make_register_schema(**overrides):
    defaults = {
        "username": name,
        "email": email,
        "password": password,
    }
    params = {**defaults, **overrides}
    return schemas.RegisterRequestSchema(**params)


def make_register_payload(**overrides):
    return make_register_schema(**overrides).model_dump()


def make_login_schema(**overrides):
    defaults = {
        "email": email,
        "password": password,
    }
    params = {**defaults, **overrides}
    return schemas.LoginRequestSchema(**params)


def make_login_payload(**overrides):
    return make_login_schema(**overrides).model_dump()
