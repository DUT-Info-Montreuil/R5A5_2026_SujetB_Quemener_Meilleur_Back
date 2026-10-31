from typing import List, Optional

from fastapi import APIRouter, HTTPException, status

from backTournoi.main.dto.message_dto import MessageCreate, MessageOut
from backTournoi.main.services.message_service import MessageService

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.get("/", response_model=List[MessageOut])
def get_messages(equipe_id: Optional[int] = None):
    """Retourne la liste des messages (filtrable par équipe avec ?equipe_id=)."""
    return MessageService.lister_messages(equipe_id)


@router.post("/", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def post_message(payload: MessageCreate):
    """Poste un nouveau message dans une équipe."""
    try:
        return MessageService.creer_message(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{message_id}", response_model=MessageOut)
def get_message_detail(message_id: int):
    """Retourne un message par son ID."""
    message = MessageService.obtenir_message(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message introuvable")
    return message