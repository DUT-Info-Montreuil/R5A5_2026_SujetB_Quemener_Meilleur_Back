from typing import List, Optional

from ..utils.data.data import tournois, matchs, get_equipe, get_tournoi
from ..dto.tournoi_dto import TournoiCreate, TournoiUpdate

# Transitions de statut autorisées
TRANSITIONS = {
    "OUVERT": {"FERME", "TERMINE"},
    "FERME": {"EN_COURS", "TERMINE"},
    "EN_COURS": {"TERMINE"},
    "TERMINE": set(),
}


class TournoiService:
    """Contient toute la logique métier liée aux tournois."""

    @staticmethod
    def lister_tournois() -> List[dict]:
        """Retourne la liste brute de tous les tournois."""
        return tournois

    @staticmethod
    def obtenir_tournoi(tournoi_id: int) -> Optional[dict]:
        """Retourne un tournoi par son ID, sans enrichissement."""
        return get_tournoi(tournoi_id)

    @staticmethod
    def obtenir_tournoi_detail(tournoi_id: int) -> Optional[dict]:
        """Retourne un tournoi enrichi avec ses équipes et ses matchs."""
        tournoi = get_tournoi(tournoi_id)
        if not tournoi:
            return None

        equipes_ids = tournoi["equipes_ids"]
        tournoi_equipes = [e for e in (get_equipe(eid) for eid in equipes_ids) if e]
        tournoi_matchs = [
            m for m in matchs
            if m["equipe1_id"] in equipes_ids or m["equipe2_id"] in equipes_ids
        ]

        return {
            **tournoi,
            "equipes": tournoi_equipes,
            "matchs": tournoi_matchs,
        }

    @staticmethod
    def creer_tournoi(payload: TournoiCreate) -> dict:
        """Crée un nouveau tournoi (statut OUVERT, sans équipe)."""
        nouvel_id = max((t["id"] for t in tournois), default=0) + 1

        nouveau_tournoi = {
            "id": nouvel_id,
            "nom": payload.nom,
            "description": payload.description,
            "statut": "OUVERT",
            "jeu_id": payload.jeu_id,
            "equipes_ids": [],
        }

        tournois.append(nouveau_tournoi)
        return nouveau_tournoi

    @staticmethod
    def modifier_tournoi(tournoi_id: int, payload: TournoiUpdate) -> Optional[dict]:
        """Modifie partiellement un tournoi (dont son statut).
        Retourne None si le tournoi n'existe pas, lève ValueError si la modification est invalide."""
        tournoi = get_tournoi(tournoi_id)
        if not tournoi:
            return None

        changements = payload.model_dump(mode="json", exclude_unset=True)

        for champ in ("nom", "date_debut", "date_fin", "statut"):
            if champ in changements and changements[champ] is None:
                raise ValueError(f"Le champ '{champ}' ne peut pas être null.")

        if "statut" in changements:
            actuel, nouveau = tournoi["statut"], changements["statut"]
            if nouveau != actuel and nouveau not in TRANSITIONS.get(actuel, set()):
                raise ValueError(f"Transition de statut interdite : {actuel} -> {nouveau}.")

        debut = changements.get("date_debut", tournoi.get("date_debut"))
        fin = changements.get("date_fin", tournoi.get("date_fin"))
        if debut is not None and fin is not None and fin < debut:
            raise ValueError("date_fin doit être postérieure ou égale à date_debut.")

        tournoi.update(changements)
        return tournoi
