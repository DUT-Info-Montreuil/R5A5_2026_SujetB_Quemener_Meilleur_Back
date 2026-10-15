import os
import time
from typing import Optional

import bcrypt
import jwt

# En prod : définir JWT_SECRET_KEY dans l'environnement (ex. `openssl rand -hex 32`)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-change-me")
ALGORITHM = "HS256"
TOKEN_TTL_SECONDS = 60 * 60 * 8  # 8 h


def _encode(mot_de_passe: str) -> bytes:
    raw = mot_de_passe.encode("utf-8")
    if len(raw) > 72:  # limite de bcrypt
        raise ValueError("Le mot de passe est trop long (72 octets maximum).")
    return raw


def hash_password(mot_de_passe: str) -> str:
    return bcrypt.hashpw(_encode(mot_de_passe), bcrypt.gensalt()).decode()


def verify_password(mot_de_passe: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_encode(mot_de_passe), hashed.encode())
    except ValueError:
        return False


def is_hashed(value: str) -> bool:
    """Vrai si la valeur ressemble à un hash bcrypt (et non à un mot de passe en clair)."""
    return value.startswith(("$2a$", "$2b$", "$2y$"))


# Hash factice : temps de réponse similaire quand le login n'existe pas
DUMMY_HASH = hash_password("dummy")


def create_token(user_id: int) -> str:
    now = int(time.time())
    return jwt.encode(
        {"sub": str(user_id), "iat": now, "exp": now + TOKEN_TTL_SECONDS},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_token(token: str) -> Optional[int]:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(data["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None