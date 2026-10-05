from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class StatutTournoi(str, Enum):
    """Statuts possibles d'un tournoi (doivent correspondre aux clés de TRANSITIONS)."""
    OUVERT = "OUVERT"
    FERME = "FERME"
    EN_COURS = "EN_COURS"
    TERMINE = "TERMINE"


class TournoiCreate(BaseModel):
    """DTO de création d'un tournoi. Un tournoi est créé sans dates (elles ne sont
    plus gérées à la création) et son statut est toujours OUVERT par défaut."""
    nom: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    jeu_id: Optional[int] = None


class TournoiUpdate(BaseModel):
    """DTO de modification partielle d'un tournoi (PATCH)."""
    nom: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = None
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None
    jeu_id: Optional[int] = None
    statut: Optional[StatutTournoi] = None


class EquipeOut(BaseModel):
    """Représentation d'une équipe telle qu'exposée par l'API."""
    id: int
    nom: str
    tournoi_id: int
    joueurs_ids: List[int] = []

    model_config = {"from_attributes": True}


class MatchOut(BaseModel):
    """Représentation d'un match telle qu'exposée par l'API."""
    id: int
    date: str
    equipe1_id: int
    equipe2_id: int
    score_equipe1: int
    score_equipe2: int

    model_config = {"from_attributes": True}


class TournoiOut(BaseModel):
    """DTO de sortie pour un tournoi (liste, création, modification)."""
    id: int
    nom: str
    description: Optional[str] = None
    statut: StatutTournoi
    jeu_id: Optional[int] = None
    equipes_ids: List[int] = []

    model_config = {"from_attributes": True}


class TournoiDetailOut(TournoiOut):
    """DTO de sortie pour le détail enrichi d'un tournoi (équipes + matchs)."""
    equipes: List[EquipeOut] = []
    matchs: List[MatchOut] = []