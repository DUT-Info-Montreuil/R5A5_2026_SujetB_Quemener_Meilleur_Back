from typing import Optional

from pydantic import BaseModel


class MatchCreate(BaseModel):
    """Données attendues pour créer un match (POST /match)."""
    equipe1_id: int
    equipe2_id: int
    score_equipe1: int = 0
    score_equipe2: int = 0


class MatchUpdate(BaseModel):
    """Données modifiables d'un match (PUT /match/{match_id}).
    Tous les champs sont optionnels : seuls ceux envoyés sont modifiés."""
    equipe1_id: Optional[int] = None
    equipe2_id: Optional[int] = None
    score_equipe1: Optional[int] = None
    score_equipe2: Optional[int] = None


class MatchResponse(BaseModel):
    """Données renvoyées au client."""
    id: int
    equipe1_id: int
    equipe2_id: int
    score_equipe1: int
    score_equipe2: int
