from typing import List

from fastapi import APIRouter, HTTPException, status

from ..dto.match_dto import MatchCreate, MatchResponse, MatchUpdate
from ..services.match_service import MatchService

router = APIRouter(prefix="/match", tags=["Match"])


@router.get("", response_model=List[MatchResponse])
def get_matchs():
    return MatchService.lister_matchs()


@router.post("", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(payload: MatchCreate):
    try:
        return MatchService.creer_match(payload)
    except ValueError as erreur:
        raise HTTPException(status_code=400, detail=str(erreur))


@router.put("/{match_id}", response_model=MatchResponse)
def update_match(match_id: int, payload: MatchUpdate):
    try:
        match = MatchService.modifier_match(match_id, payload)
    except ValueError as erreur:
        raise HTTPException(status_code=400, detail=str(erreur))
    if match is None:
        raise HTTPException(status_code=404, detail="Match introuvable")
    return match