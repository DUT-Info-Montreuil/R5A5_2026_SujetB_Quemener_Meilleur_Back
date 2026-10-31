from typing import List, Optional

from ..repo.equipe_repository import EquipeRepository
from ..repo.match_repository import MatchRepository
from ..repo.tournoi_repository import TournoiRepository
from ..utils.data.transaction import transaction
from ..dto.tournoi_dto import TournoiCreate, TournoiUpdate
from .bracket_service import BracketService

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
        with transaction() as conn:
            return TournoiRepository.lister(conn)

    @staticmethod
    def obtenir_tournoi(tournoi_id: int) -> Optional[dict]:
        """Retourne un tournoi par son ID, sans enrichissement."""
        with transaction() as conn:
            return TournoiRepository.obtenir(conn, tournoi_id)

    @staticmethod
    def obtenir_tournoi_detail(tournoi_id: int) -> Optional[dict]:
        """Retourne un tournoi enrichi avec ses équipes et ses matchs."""
        with transaction() as conn:
            tournoi = TournoiRepository.obtenir(conn, tournoi_id)
            if not tournoi:
                return None

            tournoi_equipes = EquipeRepository.lister_par_tournoi(conn, tournoi_id)
            tournoi_matchs = MatchRepository.lister_par_tournoi(conn, tournoi_id)

        return {
            **tournoi,
            "equipes": tournoi_equipes,
            "matchs": tournoi_matchs,
        }

    @staticmethod
    def creer_tournoi(payload: TournoiCreate) -> dict:
        """Crée un nouveau tournoi (statut OUVERT, sans équipe)."""
        with transaction() as conn:
            return TournoiRepository.creer(
                conn,
                nom=payload.nom,
                description=payload.description,
                petite_finale=payload.petite_finale,
                statut="OUVERT",
            )

    @staticmethod
    def modifier_tournoi(tournoi_id: int, payload: TournoiUpdate) -> Optional[dict]:
        """Modifie partiellement un tournoi (dont son statut).
        Le passage à EN_COURS génère l'arbre (une seule fois).
        Retourne None si le tournoi n'existe pas, lève ValueError si la modification est invalide."""
        with transaction() as conn:
            tournoi = TournoiRepository.obtenir(conn, tournoi_id)
            if not tournoi:
                return None

            changements = payload.model_dump(mode="json", exclude_unset=True)

            for champ in ("nom", "statut", "petite_finale"):
                if champ in changements and changements[champ] is None:
                    raise ValueError(f"Le champ '{champ}' ne peut pas être null.")

            if "petite_finale" in changements and tournoi["statut"] in ("EN_COURS", "TERMINE"):
                raise ValueError("L'option petite finale ne peut plus être modifiée une fois le tournoi démarré.")

            passe_en_cours = False
            if "statut" in changements:
                actuel, nouveau = tournoi["statut"], changements["statut"]
                if nouveau != actuel and nouveau not in TRANSITIONS.get(actuel, set()):
                    raise ValueError(f"Transition de statut interdite : {actuel} -> {nouveau}.")
                passe_en_cours = nouveau == "EN_COURS" and actuel != "EN_COURS"

            # Génération en dernier : si elle échoue (ex. < 2 équipes), rien n'a été modifié
            # (la transaction est annulée).
            if passe_en_cours:
                BracketService.generer({**tournoi, **changements}, conn)

            return TournoiRepository.modifier(conn, tournoi_id, changements)
