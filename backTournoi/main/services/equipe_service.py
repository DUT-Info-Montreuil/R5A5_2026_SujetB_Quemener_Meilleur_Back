from typing import List, Optional

from ..utils.data.data  import equipes, matchs, messages, get_equipe, get_tournoi, get_utilisateur
from ..dto.equipe_dto import EquipeCreate


class EquipeService:
    """Contient toute la logique métier liée aux équipes."""

    @staticmethod
    def lister_equipes() -> List[dict]:
        """Retourne la liste brute de toutes les équipes."""
        return equipes

    @staticmethod
    def obtenir_equipe(equipe_id: int) -> Optional[dict]:
        """Retourne une équipe par son ID, sans enrichissement."""
        return get_equipe(equipe_id)

    @staticmethod
    def obtenir_equipe_detail(equipe_id: int) -> Optional[dict]:
        """Retourne une équipe enrichie avec son tournoi, ses joueurs,
        ses matchs et ses messages."""
        equipe = get_equipe(equipe_id)
        if not equipe:
            return None

        joueurs = [get_utilisateur(uid) for uid in equipe["joueurs_ids"]]
        tournoi = get_tournoi(equipe["tournoi_id"])

        equipe_matchs = [
            m for m in matchs
            if m["equipe1_id"] == equipe_id or m["equipe2_id"] == equipe_id
        ]
        equipe_messages = [m for m in messages if m["equipe_id"] == equipe_id]

        return {
            **equipe,
            "tournoi": tournoi,
            "joueurs": joueurs,
            "matchs": equipe_matchs,
            "messages": equipe_messages,
        }

    @staticmethod
    def creer_equipe(payload: EquipeCreate) -> dict:
        """Crée une nouvelle équipe et l'ajoute au tournoi correspondant."""
        if not get_tournoi(payload.tournoi_id):
            raise ValueError(f"Le tournoi {payload.tournoi_id} n'existe pas.")

        nouvel_id = max((e["id"] for e in equipes), default=0) + 1

        nouvelle_equipe = {
            "id": nouvel_id,
            "nom": payload.nom,
            "tournoi_id": payload.tournoi_id,
            "joueurs_ids": payload.joueurs_ids,
        }

        equipes.append(nouvelle_equipe)

        # On met aussi à jour la liste des équipes du tournoi concerné
        tournoi = get_tournoi(payload.tournoi_id)
        if tournoi is not None:
            tournoi["equipes_ids"].append(nouvel_id)

        return nouvelle_equipe
