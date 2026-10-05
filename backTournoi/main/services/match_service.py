from typing import List, Optional

from ..utils.data.data import matchs, get_equipe
from ..dto.match_dto import MatchCreate, MatchUpdate


class MatchService:
    """Contient toute la logique métier liée aux matchs."""

    @staticmethod
    def lister_matchs() -> List[dict]:
        """Retourne la liste brute de tous les matchs."""
        return matchs

    @staticmethod
    def creer_match(payload: MatchCreate) -> dict:
        """Crée un nouveau match entre deux équipes existantes."""
        MatchService._verifier_equipes(payload.equipe1_id, payload.equipe2_id)

        nouvel_id = max((m["id"] for m in matchs), default=0) + 1

        nouveau_match = {
            "id": nouvel_id,
            "equipe1_id": payload.equipe1_id,
            "equipe2_id": payload.equipe2_id,
            "score_equipe1": payload.score_equipe1,
            "score_equipe2": payload.score_equipe2,
        }

        matchs.append(nouveau_match)
        return nouveau_match

    @staticmethod
    def modifier_match(match_id: int, payload: MatchUpdate) -> Optional[dict]:
        """Modifie un match existant (seuls les champs envoyés sont modifiés).
        Retourne None si le match n'existe pas."""
        match = next((m for m in matchs if m["id"] == match_id), None)
        if match is None:
            return None

        modifications = payload.model_dump(exclude_none=True)

        # On vérifie les équipes telles qu'elles seront après la modification
        MatchService._verifier_equipes(
            modifications.get("equipe1_id", match["equipe1_id"]),
            modifications.get("equipe2_id", match["equipe2_id"]),
        )

        match.update(modifications)
        return match

    @staticmethod
    def _verifier_equipes(equipe1_id: int, equipe2_id: int) -> None:
        """Vérifie que les deux équipes existent et sont différentes."""
        if equipe1_id == equipe2_id:
            raise ValueError("Un match doit opposer deux équipes différentes.")
        for equipe_id in (equipe1_id, equipe2_id):
            if not get_equipe(equipe_id):
                raise ValueError(f"L'équipe {equipe_id} n'existe pas.")