import hmac
from typing import Optional

from backTournoi.main.utils.data.data import utilisateurs
from backTournoi.main.utils.security import (
    DUMMY_HASH,
    create_token,
    decode_token,
    hash_password,
    is_hashed,
    verify_password,
)
from backTournoi.main.dto.auth_dto import RegisterPayload
from backTournoi.main.dto.utilisateur_dto import UtilisateurCreate
from backTournoi.main.services.utilisateur_service import UtilisateurService


class AuthService:
    @staticmethod
    def register(payload: RegisterPayload) -> dict:
        """Crée un compte NON administrateur (le hachage est fait dans
        UtilisateurService). Lève ValueError si le login existe déjà."""
        return UtilisateurService.creer_utilisateur(
            UtilisateurCreate(
                login=payload.login.strip(),
                mdp=payload.mot_de_passe,
                is_admin=False,
            )
        )

    @staticmethod
    def authenticate(login: str, mot_de_passe: str) -> Optional[dict]:
        user = next((u for u in utilisateurs if u["login"] == login.strip()), None)
        if user is None:
            verify_password(mot_de_passe, DUMMY_HASH)  # temps de réponse constant
            return None

        stored = user["mdp"]
        if is_hashed(stored):
            ok = verify_password(mot_de_passe, stored)
        else:
            # Utilisateur de départ (data.py) encore en clair : on compare,
            # puis on remplace par un hash dès la première connexion réussie.
            ok = hmac.compare_digest(stored.encode(), mot_de_passe.encode())
            if ok:
                user["mdp"] = hash_password(mot_de_passe)

        return user if ok else None

    @staticmethod
    def create_token(user_id: int) -> str:
        return create_token(user_id)

    @staticmethod
    def decode_token(token: str) -> Optional[int]:
        return decode_token(token)
