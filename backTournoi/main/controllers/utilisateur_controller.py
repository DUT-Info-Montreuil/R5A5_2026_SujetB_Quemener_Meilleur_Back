from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from backTournoi.main.dto.utilisateur_dto import (
    UtilisateurCreate,
    UtilisateurUpdate,
    UtilisateurOut,
    UtilisateurDetailOut,
)
from backTournoi.main.services.auth_dependencies import get_current_user
from backTournoi.main.services.utilisateur_service import UtilisateurService

router = APIRouter(prefix="/utilisateurs", tags=["Utilisateurs"])


@router.get("/", response_model=List[UtilisateurOut])
def get_utilisateurs():
    """Retourne la liste de tous les utilisateurs."""
    return UtilisateurService.lister_utilisateurs()


@router.post("/", response_model=UtilisateurOut, status_code=status.HTTP_201_CREATED)
def post_utilisateur(payload: UtilisateurCreate):
    """Crée un nouvel utilisateur (le mot de passe est haché par le service).
    Redondant avec /auth/register : peut être supprimé."""
    try:
        return UtilisateurService.creer_utilisateur(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{utilisateur_id}", response_model=UtilisateurDetailOut)
def get_utilisateur_detail(utilisateur_id: int):
    """Retourne le détail d'un utilisateur (équipes, messages)."""
    utilisateur = UtilisateurService.obtenir_utilisateur_detail(utilisateur_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return utilisateur


@router.patch("/{utilisateur_id}", response_model=UtilisateurOut)
def patch_utilisateur(
    utilisateur_id: int,
    payload: UtilisateurUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Modifie partiellement un utilisateur. Chacun ne peut modifier que son propre compte."""
    if current_user["id"] != utilisateur_id:
        raise HTTPException(
            status_code=403, detail="Vous ne pouvez modifier que votre propre compte."
        )
    try:
        utilisateur = UtilisateurService.modifier_utilisateur(utilisateur_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return utilisateur