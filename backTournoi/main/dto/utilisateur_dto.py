from typing import List, Optional

from pydantic import BaseModel, Field

from backTournoi.main.dto.equipe_dto import EquipeOut
from backTournoi.main.dto.message_dto import MessageOut


class UtilisateurCreate(BaseModel):
    """Données nécessaires pour créer un utilisateur."""
    login: str = Field(..., min_length=1, max_length=50)
    mdp: str = Field(..., min_length=1, max_length=50)
    is_admin: bool = False


class UtilisateurUpdate(BaseModel):
    """Données modifiables d'un utilisateur (PATCH : tous les champs sont optionnels)."""
    login: Optional[str] = Field(None, min_length=1, max_length=50)
    mdp: Optional[str] = Field(None, min_length=1, max_length=50)
    is_admin: Optional[bool] = None


class UtilisateurOut(BaseModel):
    """Représentation d'un utilisateur renvoyée par l'API.
    Le mot de passe (mdp) n'est volontairement jamais exposé."""
    id: int
    login: str
    is_admin: bool = False


class UtilisateurDetailOut(UtilisateurOut):
    """Utilisateur enrichi avec ses équipes et ses messages."""
    equipes: List[EquipeOut] = []
    messages: List[MessageOut] = []
