from typing import List

from fastapi import APIRouter, HTTPException, status

from ..dto.tournoi_dto import TournoiCreate, TournoiUpdate, TournoiOut, TournoiDetailOut
from ..services.tournoi_service import TournoiService

router = APIRouter(prefix="/tournois", tags=["Tournois"])


@router.get("/", response_model=List[TournoiOut])
def get_tournois():
    """Retourne la liste de tous les tournois."""
    return TournoiService.lister_tournois()


@router.post("/", response_model=TournoiOut, status_code=status.HTTP_201_CREATED)
def post_tournoi(payload: TournoiCreate):
    """Crée un nouveau tournoi."""
    try:
        return TournoiService.creer_tournoi(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{tournoi_id}", response_model=TournoiDetailOut)
def get_tournoi_detail(tournoi_id: int):
    """Retourne le détail d'un tournoi (équipes, matchs)."""
    tournoi = TournoiService.obtenir_tournoi_detail(tournoi_id)
    if not tournoi:
        raise HTTPException(status_code=404, detail="Tournoi introuvable")
    return tournoi


@router.patch("/{tournoi_id}", response_model=TournoiOut)
def patch_tournoi(tournoi_id: int, payload: TournoiUpdate):
    """Modifie partiellement un tournoi (dont son statut)."""
    try:
        tournoi = TournoiService.modifier_tournoi(tournoi_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not tournoi:
        raise HTTPException(status_code=404, detail="Tournoi introuvable")
    return tournoi
