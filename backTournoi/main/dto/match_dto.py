from typing import List, Optional

from pydantic import BaseModel, Field


class MatchOut(BaseModel):
    id: int
    tournoi_id: int
    round: int
    position: int
    equipe1_id: Optional[int] = None
    equipe2_id: Optional[int] = None
    score_equipe1: Optional[int] = None
    score_equipe2: Optional[int] = None
    vainqueur_id: Optional[int] = None
    next_match_id: Optional[int] = None
    next_slot: Optional[int] = None
    loser_next_match_id: Optional[int] = None
    loser_next_slot: Optional[int] = None
    petite_finale: bool = False
    bye: bool = False


class MatchScoreUpdate(BaseModel):
    """Saisie / correction d'un résultat (scores = manches gagnées)."""
    score_equipe1: int = Field(ge=0)
    score_equipe2: int = Field(ge=0)


class ArbreMatchOut(MatchOut):
    equipe1_nom: Optional[str] = None
    equipe2_nom: Optional[str] = None


class ArbreRoundOut(BaseModel):
    round: int
    titre: str
    matchs: List[ArbreMatchOut]


class ArbreOut(BaseModel):
    tournoi_id: int
    rounds: List[ArbreRoundOut]
    petite_finale: Optional[ArbreMatchOut] = None
