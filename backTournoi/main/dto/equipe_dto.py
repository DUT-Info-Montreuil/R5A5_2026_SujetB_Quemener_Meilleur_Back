from typing import List, Optional

from pydantic import BaseModel, Field

# Même DTO de match que pour /matchs et /tournois : les matchs de l'arbre n'ont pas
# de date et ont des scores/équipes à None tant qu'ils ne sont pas joués.
from backTournoi.main.dto.match_dto import MatchOut


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
    is_admin: Optional[bool] = False


class MessageOut(BaseModel):
    id: int
    message: str
    utilisateur_id: int
    equipe_id: int


class EquipeDetailOut(EquipeOut):
    """DTO enrichi utilisé pour GET /equipes/{id}.

    `messages` vaut None quand l'appelant n'a pas le droit de lire le chat de
    l'équipe (visiteur, ou utilisateur connecté non membre), et [] quand le chat
    est lisible mais vide."""

    tournoi: Optional[dict] = None
    joueurs: List[Optional[JoueurOut]] = []
    matchs: List[MatchOut] = []
    messages: Optional[List[MessageOut]] = None
