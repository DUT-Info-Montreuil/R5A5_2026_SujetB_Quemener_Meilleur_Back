from typing import List

from fastapi import APIRouter, Depends, HTTPException

from backTournoi.main.dto.match_dto import MatchOut, MatchScoreUpdate
from backTournoi.main.services.auth_dependencies import get_current_admin
from backTournoi.main.services.match_service import MatchService

router = APIRouter(prefix="/matchs", tags=["Matchs"])


@router.get("/", response_model=List[MatchOut])
def get_matchs():
    """Retourne la liste de tous les matchs."""
    return MatchService.lister_matchs()


@router.get("/{match_id}", response_model=MatchOut)
def get_match_detail(match_id: int):
    match = MatchService.obtenir_match(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match introuvable")
    return match


@router.patch("/{match_id}", response_model=MatchOut, dependencies=[Depends(get_current_admin)])
def patch_match(match_id: int, payload: MatchScoreUpdate):
    """Saisit ou corrige le score d'un match (admin). Le vainqueur avance automatiquement."""
    try:
        match = MatchService.enregistrer_score(match_id, payload.score_equipe1, payload.score_equipe2)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not match:
        raise HTTPException(status_code=404, detail="Match introuvable")
    return match
