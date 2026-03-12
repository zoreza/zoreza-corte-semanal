from zoreza.db.queries import fetchone
from zoreza.services.passwords import verify_password

def authenticate(username: str, password: str):
    user = fetchone("SELECT * FROM usuarios WHERE username=? AND activo=1", (username,))
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user
