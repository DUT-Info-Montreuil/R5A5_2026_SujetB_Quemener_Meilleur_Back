from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backTournoi.main.services.auth_service import AuthService
from backTournoi.main.utils.data.data import get_utilisateur

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    """Exige un jeton valide et renvoie l'utilisateur connecté."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentification requise.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    user_id = AuthService.decode_token(credentials.credentials)
    if user_id is None:
        raise unauthorized

    user = get_utilisateur(user_id)
    if not user:
        raise unauthorized
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
