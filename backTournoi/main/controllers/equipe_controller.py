from typing import List

from fastapi import APIRouter, HTTPException, status

from ..dto.equipe_dto import EquipeCreate, EquipeOut, EquipeDetailOut
from ..services.equipe_service import EquipeService

router = APIRouter(prefix="/equipes", tags=["Equipes"])


@router.get("/", response_model=List[EquipeOut])
def get_equipes():
    """Retourne la liste de toutes les équipes."""
    return EquipeService.lister_equipes()


@router.post("/", response_model=EquipeOut, status_code=status.HTTP_201_CREATED)
def post_equipe(payload: EquipeCreate):
    """Crée une nouvelle équipe."""
    try:
        return EquipeService.creer_equipe(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{equipe_id}", response_model=EquipeDetailOut)
def get_equipe_detail(equipe_id: int):
    """Retourne le détail d'une équipe (tournoi, joueurs, matchs, messages)."""
    equipe = EquipeService.obtenir_equipe_detail(equipe_id)
    if not equipe:
        raise HTTPException(status_code=404, detail="Equipe introuvable")
    return equipe
