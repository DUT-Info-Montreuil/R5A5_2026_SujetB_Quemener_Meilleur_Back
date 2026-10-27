from typing import List, Optional

from ..utils.data.data import matchs, get_match, get_tournoi


class MatchService:
    """Logique métier des matchs : saisie des scores et progression dans l'arbre."""

    @staticmethod
    def lister_matchs() -> List[dict]:
        return matchs

    @staticmethod
    def obtenir_match(match_id: int) -> Optional[dict]:
        return get_match(match_id)

    @staticmethod
    def enregistrer_score(match_id: int, score1: int, score2: int) -> Optional[dict]:
        """Saisit ou corrige un score, puis fait avancer vainqueur (et perdant si petite finale).
        Retourne None si le match n'existe pas, lève ValueError si la saisie est invalide."""
        match = get_match(match_id)
        if not match:
            return None

        tournoi = get_tournoi(match["tournoi_id"])
        if not tournoi or tournoi["statut"] != "EN_COURS":
            raise ValueError("Les scores ne peuvent être saisis que lorsque le tournoi est En cours.")
        if match["bye"]:
            raise ValueError("Ce match est un qualifié d'office : il n'y a pas de score à saisir.")
        e1, e2 = match["equipe1_id"], match["equipe2_id"]
        if e1 is None or e2 is None:
            raise ValueError("Ce match n'a pas encore ses deux équipes.")
        if score1 < 0 or score2 < 0:
            raise ValueError("Un score ne peut pas être négatif.")
        if score1 == score2:
            raise ValueError("Match nul impossible en élimination directe.")

        vainqueur, perdant = (e1, e2) if score1 > score2 else (e2, e1)

        destinations = [
            (match["next_match_id"], match["next_slot"], vainqueur),
            (match["loser_next_match_id"], match["loser_next_slot"], perdant),
        ]

        # Correction qui change le vainqueur : refusée si un match aval est déjà joué
        if match["vainqueur_id"] is not None and match["vainqueur_id"] != vainqueur:
            for dest_id, _, _ in destinations:
                dest = get_match(dest_id) if dest_id else None
                if dest and dest["score_equipe1"] is not None:
                    raise ValueError(
                        "Correction impossible : le match suivant a déjà un résultat. "
                        "Corrigez d'abord celui-ci."
                    )

        match["score_equipe1"] = score1
        match["score_equipe2"] = score2
        match["vainqueur_id"] = vainqueur

        for dest_id, slot, equipe_id in destinations:
            dest = get_match(dest_id) if dest_id else None
            if dest:
                dest[f"equipe{slot}_id"] = equipe_id

        return match
