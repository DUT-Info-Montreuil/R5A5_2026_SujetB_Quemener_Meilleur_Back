from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from backTournoi.main.dto.equipe_dto import EquipeCreate, EquipeOut, EquipeDetailOut
from backTournoi.main.services.auth_dependencies import get_current_non_admin, get_optional_user
from backTournoi.main.services.equipe_service import EquipeService

router = APIRouter(prefix="/equipes", tags=["Equipes"])


@router.get("/", response_model=List[EquipeOut])
def get_equipes():
    """Retourne la liste de toutes les équipes (public)."""
    return EquipeService.lister_equipes()


@router.post(
    "/",
    response_model=EquipeOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_non_admin)],  # connecté et non-admin
)
def post_equipe(payload: EquipeCreate):
    """Crée une nouvelle équipe (réservé aux utilisateurs connectés non-administrateurs)."""
    try:
        return EquipeService.creer_equipe(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{equipe_id}", response_model=EquipeDetailOut)
def get_equipe_detail(
    equipe_id: int,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Retourne le détail d'une équipe (tournoi, joueurs, matchs) : public.
    Les messages du chat ne sont renvoyés qu'aux membres de l'équipe et aux admins."""
    equipe = EquipeService.obtenir_equipe(equipe_id)
    if not equipe:
        raise HTTPException(status_code=404, detail="Equipe introuvable")
    return EquipeService.obtenir_equipe_detail(
        equipe_id,
        inclure_messages=EquipeService.peut_lire_messages(equipe, current_user),
    )
