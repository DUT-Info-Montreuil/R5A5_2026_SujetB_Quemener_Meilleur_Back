from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backTournoi.main.services.auth_service import AuthService
from backTournoi.main.utils.data.data import get_utilisateur

_bearer = HTTPBearer(auto_error=False)


def _utilisateur_depuis_jeton(
    credentials: HTTPAuthorizationCredentials | None,
) -> dict | None:
    """Renvoie l'utilisateur correspondant au jeton, ou None si le jeton est
    absent, invalide, expiré ou si l'utilisateur n'existe plus."""
    if credentials is None:
        return None

    user_id = AuthService.decode_token(credentials.credentials)
    if user_id is None:
        return None

    return get_utilisateur(user_id) or None


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict | None:
    """Pour les routes publiques : renvoie l'utilisateur connecté, ou None pour un
    visiteur. Ne lève jamais 401 (un jeton invalide ou expiré = simple visiteur)."""
    return _utilisateur_depuis_jeton(credentials)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    """Exige un jeton valide et renvoie l'utilisateur connecté."""
    user = _utilisateur_depuis_jeton(credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_non_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Comme get_current_user, mais refuse les administrateurs (403)."""
    if current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Un administrateur ne peut pas créer ou rejoindre une équipe.",
        )
    return current_user


def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Comme get_current_user, mais réservé aux administrateurs (403 sinon)."""
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action réservée aux administrateurs.",
        )
    return current_user
