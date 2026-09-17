from typing import List, Optional

from pydantic import BaseModel, Field


class EquipeCreate(BaseModel):
    """DTO utilisé en entrée du POST /equipes/ pour créer une équipe."""

    nom: str = Field(..., min_length=1, description="Nom de l'équipe")
    tournoi_id: int = Field(..., description="ID du tournoi auquel l'équipe est rattachée")
    joueurs_ids: List[int] = Field(
        default_factory=list,
        description="Liste des IDs des joueurs (utilisateurs) de l'équipe",
    )


class EquipeOut(BaseModel):
    """DTO utilisé en sortie pour représenter une équipe (liste et création)."""

    id: int
    nom: str
    tournoi_id: int
    joueurs_ids: List[int]


class JoueurOut(BaseModel):
    id: int
    login: str
    isAdmin: Optional[bool] = False


class MatchOut(BaseModel):
    id: int
    date: str
    equipe1_id: int
    equipe2_id: int
    score_equipe1: int
    score_equipe2: int


class MessageOut(BaseModel):
    id: int
    message: str
    date: str
    utilisateur_id: int
    equipe_id: int


class EquipeDetailOut(EquipeOut):
    """DTO enrichi utilisé pour GET /equipes/{id}."""

    tournoi: Optional[dict] = None
    joueurs: List[Optional[JoueurOut]] = []
    matchs: List[MatchOut] = []
    messages: List[MessageOut] = []
