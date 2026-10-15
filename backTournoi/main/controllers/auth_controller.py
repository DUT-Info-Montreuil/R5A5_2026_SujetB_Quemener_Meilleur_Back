from fastapi import APIRouter, Depends, HTTPException, status

from backTournoi.main.dto.auth_dto import (
    AuthUserOut,
    LoginPayload,
    RegisterPayload,
    TokenOut,
)
from backTournoi.main.services.auth_service import AuthService
from backTournoi.main.services.auth_dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


def _token_response(user: dict) -> TokenOut:
    return TokenOut(
        access_token=AuthService.create_token(user["id"]),
        utilisateur=AuthUserOut(
            id=user["id"], login=user["login"], is_admin=user.get("is_admin", False)
        ),
    )


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterPayload):
    """Crée un compte et connecte directement l'utilisateur."""
    try:
        user = AuthService.register(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _token_response(user)


@router.post("/login", response_model=TokenOut)
def login(payload: LoginPayload):
    user = AuthService.authenticate(payload.login, payload.mot_de_passe)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login ou mot de passe incorrect.",
        )
    return _token_response(user)


@router.get("/me", response_model=AuthUserOut)
def me(current_user: dict = Depends(get_current_user)):
    return AuthUserOut(
        id=current_user["id"],
        login=current_user["login"],
        is_admin=current_user.get("is_admin", False),
    )