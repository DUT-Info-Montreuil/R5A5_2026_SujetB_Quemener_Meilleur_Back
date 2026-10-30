from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from backTournoi.main.dto.demande_dto import DemandeCreate, DemandeOut
from backTournoi.main.services.auth_dependencies import get_current_non_admin
from backTournoi.main.services.demande_service import DemandeService

router = APIRouter(prefix="/demandes", tags=["Demandes"])


@router.get("/", response_model=List[DemandeOut])
def get_demandes(equipe_id: Optional[int] = None):
    """Retourne les demandes d'adhésion (filtrables par équipe)."""
    return DemandeService.lister_demandes(equipe_id)


@router.post(
    "/",
    response_model=DemandeOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_non_admin)],  # les admins ne rejoignent pas d'équipe
)
def post_demande(payload: DemandeCreate):
    """Crée une demande d'adhésion à une équipe (à valider par le capitaine)."""
    try:
        return DemandeService.creer_demande(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _traiter(action, demande_id: int, current_user):
    """Appelle le service et traduit les erreurs en codes HTTP."""
    try:
        return action(demande_id, current_user["id"])
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{demande_id}/accepter", response_model=DemandeOut)
def accepter_demande(demande_id: int, current_user=Depends(get_current_non_admin)):
    """Accepte une demande d'adhésion (réservé au capitaine de l'équipe)."""
    return _traiter(DemandeService.accepter_demande, demande_id, current_user)


@router.patch("/{demande_id}/refuser", response_model=DemandeOut)
def refuser_demande(demande_id: int, current_user=Depends(get_current_non_admin)):
    """Refuse une demande d'adhésion (réservé au capitaine de l'équipe)."""
    return _traiter(DemandeService.refuser_demande, demande_id, current_user)