from typing import List, Optional

# ⚠️ À ADAPTER : chemin du module qui contient tes données fictives
from backTournoi.main.utils.data.data import (
    demandes,
    get_demande,
    get_equipe,
    get_tournoi,
    get_utilisateur,
)
from backTournoi.main.dto.demande_dto import DemandeCreate


class DemandeService:
    @staticmethod
    def lister_demandes(equipe_id: Optional[int] = None) -> List[dict]:
        """Liste les demandes, éventuellement filtrées par équipe."""
        if equipe_id is None:
            return demandes
        return [d for d in demandes if d["equipe_id"] == equipe_id]

    @staticmethod
    def creer_demande(payload: DemandeCreate) -> dict:
        """Crée une demande d'adhésion (statut EN_ATTENTE), à valider par le capitaine."""
        equipe = get_equipe(payload.equipe_id)
        if not equipe:
            raise ValueError("Equipe introuvable")

        if not get_utilisateur(payload.utilisateur_id):
            raise ValueError("Utilisateur introuvable")

        if payload.utilisateur_id in equipe["joueurs_ids"]:
            raise ValueError("Vous faites déjà partie de cette équipe")

        tournoi = get_tournoi(equipe["tournoi_id"])
        if tournoi and tournoi["statut"] != "OUVERT":
            raise ValueError("Les inscriptions de ce tournoi sont closes")

        deja_en_attente = any(
            d["equipe_id"] == payload.equipe_id
            and d["utilisateur_id"] == payload.utilisateur_id
            and d["statut"] == "EN_ATTENTE"
            for d in demandes
        )
        if deja_en_attente:
            raise ValueError("Une demande est déjà en attente pour cette équipe")

        demande = {
            "id": max((d["id"] for d in demandes), default=0) + 1,
            "equipe_id": payload.equipe_id,
            "utilisateur_id": payload.utilisateur_id,
            "statut": "EN_ATTENTE",
        }
        demandes.append(demande)
        return demande

    def _demande_a_traiter(demande_id: int, capitaine_id: int) -> tuple:
        """Retourne (demande, equipe) si la demande existe, est en attente et que l'appelant est le capitaine."""
        demande = get_demande(demande_id)
        if not demande:
            raise LookupError("Demande introuvable")

        equipe = get_equipe(demande["equipe_id"])
        if not equipe:
            raise LookupError("Equipe introuvable")

        # Le capitaine est le premier joueur de l'équipe
        if not equipe["joueurs_ids"] or equipe["joueurs_ids"][0] != capitaine_id:
            raise PermissionError("Seul le capitaine peut traiter les demandes")

        if demande["statut"] != "EN_ATTENTE":
            raise ValueError("Cette demande a déjà été traitée")

        return demande, equipe

    @staticmethod
    def accepter_demande(demande_id: int, capitaine_id: int) -> dict:
        """Accepte une demande : le joueur est ajouté à l'équipe."""
        demande, equipe = DemandeService._demande_a_traiter(demande_id, capitaine_id)

        tournoi = get_tournoi(equipe["tournoi_id"])
        if tournoi and tournoi["statut"] != "OUVERT":
            raise ValueError("Les inscriptions de ce tournoi sont closes")

        if demande["utilisateur_id"] not in equipe["joueurs_ids"]:
            equipe["joueurs_ids"].append(demande["utilisateur_id"])

        demande["statut"] = "ACCEPTEE"
        return demande

    @staticmethod
    def refuser_demande(demande_id: int, capitaine_id: int) -> dict:
        """Refuse une demande."""
        demande, _ = DemandeService._demande_a_traiter(demande_id, capitaine_id)
        demande["statut"] = "REFUSEE"
        return demande



