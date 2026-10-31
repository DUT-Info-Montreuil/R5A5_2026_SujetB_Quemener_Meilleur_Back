from typing import List, Optional

from backTournoi.main.repo.equipe_repository import EquipeRepository
from backTournoi.main.repo.message_repository import MessageRepository
from backTournoi.main.repo.utilisateur_repository import UtilisateurRepository
from backTournoi.main.utils.data.transaction import transaction
from backTournoi.main.dto.message_dto import MessageCreate


class MessageService:
    """Contient toute la logique métier liée aux messages."""

    @staticmethod
    def lister_messages(equipe_id: Optional[int] = None) -> List[dict]:
        """Retourne tous les messages, ou seulement ceux d'une équipe si
        equipe_id est fourni."""
        with transaction() as conn:
            return MessageRepository.lister(conn, equipe_id)

    @staticmethod
    def obtenir_message(message_id: int) -> Optional[dict]:
        """Retourne un message par son ID, ou None s'il n'existe pas."""
        with transaction() as conn:
            return MessageRepository.obtenir(conn, message_id)

    @staticmethod
    def creer_message(payload: MessageCreate) -> dict:
        """Crée un message dans une équipe.
        L'équipe et l'auteur doivent exister, et l'auteur doit être membre
        de l'équipe."""
        with transaction() as conn:
            equipe = EquipeRepository.obtenir(conn, payload.equipe_id)
            if not equipe:
                raise ValueError(f"L'équipe {payload.equipe_id} n'existe pas.")

            if not UtilisateurRepository.obtenir(conn, payload.utilisateur_id):
                raise ValueError(f"L'utilisateur {payload.utilisateur_id} n'existe pas.")

            if payload.utilisateur_id not in equipe["joueurs_ids"]:
                raise ValueError(
                    f"L'utilisateur {payload.utilisateur_id} n'est pas membre "
                    f"de l'équipe {payload.equipe_id}."
                )

            return MessageRepository.creer(
                conn, payload.equipe_id, payload.utilisateur_id, payload.message
            )
