from typing import List, Optional

from backTournoi.main.utils.data.data import messages, get_equipe, get_utilisateur
from backTournoi.main.dto.message_dto import MessageCreate


class MessageService:
    """Contient toute la logique métier liée aux messages."""

    @staticmethod
    def lister_messages(equipe_id: Optional[int] = None) -> List[dict]:
        """Retourne tous les messages, ou seulement ceux d'une équipe si
        equipe_id est fourni."""
        if equipe_id is None:
            return messages
        return [m for m in messages if m["equipe_id"] == equipe_id]

    @staticmethod
    def obtenir_message(message_id: int) -> Optional[dict]:
        """Retourne un message par son ID, ou None s'il n'existe pas."""
        return next((m for m in messages if m["id"] == message_id), None)

    @staticmethod
    def creer_message(payload: MessageCreate) -> dict:
        """Crée un message dans une équipe.
        L'équipe et l'auteur doivent exister, et l'auteur doit être membre
        de l'équipe."""
        equipe = get_equipe(payload.equipe_id)
        if not equipe:
            raise ValueError(f"L'équipe {payload.equipe_id} n'existe pas.")

        if not get_utilisateur(payload.utilisateur_id):
            raise ValueError(f"L'utilisateur {payload.utilisateur_id} n'existe pas.")

        if payload.utilisateur_id not in equipe["joueurs_ids"]:
            raise ValueError(
                f"L'utilisateur {payload.utilisateur_id} n'est pas membre "
                f"de l'équipe {payload.equipe_id}."
            )

        nouvel_id = max((m["id"] for m in messages), default=0) + 1

        nouveau_message = {
            "id": nouvel_id,
            "equipe_id": payload.equipe_id,
            "utilisateur_id": payload.utilisateur_id,
            "message": payload.message,
        }

        messages.append(nouveau_message)
        return nouveau_message