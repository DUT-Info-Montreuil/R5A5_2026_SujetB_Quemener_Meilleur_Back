import sqlite3
from typing import List, Optional

from backTournoi.main.repo.demande_repository import DemandeRepository
from backTournoi.main.repo.equipe_repository import EquipeRepository
from backTournoi.main.repo.tournoi_repository import TournoiRepository
from backTournoi.main.repo.utilisateur_repository import UtilisateurRepository
from backTournoi.main.utils.data.erreurs_sql import erreur_metier
from backTournoi.main.utils.data.transaction import transaction
from backTournoi.main.dto.demande_dto import DemandeCreate


class DemandeService:
    @staticmethod
    def lister_demandes(equipe_id: Optional[int] = None) -> List[dict]:
        """Liste les demandes, éventuellement filtrées par équipe."""
        with transaction() as conn:
            return DemandeRepository.lister(conn, equipe_id)

    @staticmethod
    def creer_demande(payload: DemandeCreate) -> dict:
        """Crée une demande d'adhésion (statut EN_ATTENTE), à valider par le capitaine."""
        with transaction() as conn:
            equipe = EquipeRepository.obtenir(conn, payload.equipe_id)
            if not equipe:
                raise ValueError("Equipe introuvable")

            if not UtilisateurRepository.obtenir(conn, payload.utilisateur_id):
                raise ValueError("Utilisateur introuvable")

            if payload.utilisateur_id in equipe["joueurs_ids"]:
                raise ValueError("Vous faites déjà partie de cette équipe")

            tournoi = TournoiRepository.obtenir(conn, equipe["tournoi_id"])
            if tournoi and tournoi["statut"] != "OUVERT":
                raise ValueError("Les inscriptions de ce tournoi sont closes")

            if DemandeRepository.existe_en_attente(conn, payload.equipe_id, payload.utilisateur_id):
                raise ValueError("Une demande est déjà en attente pour cette équipe")

            return DemandeRepository.creer(
                conn, payload.equipe_id, payload.utilisateur_id, "EN_ATTENTE"
            )

    def _demande_a_traiter(demande_id: int, capitaine_id: int, conn) -> tuple:
        """Retourne (demande, equipe) si la demande existe, est en attente et que l'appelant est le capitaine."""
        demande = DemandeRepository.obtenir(conn, demande_id)
        if not demande:
            raise LookupError("Demande introuvable")

        equipe = EquipeRepository.obtenir(conn, demande["equipe_id"])
        if not equipe:
            raise LookupError("Equipe introuvable")

        # Le capitaine est celui enregistré dans l'équipe (equipes.capitaine_id)
        if equipe["capitaine_id"] != capitaine_id:
            raise PermissionError("Seul le capitaine peut traiter les demandes")

        if demande["statut"] != "EN_ATTENTE":
            raise ValueError("Cette demande a déjà été traitée")

        return demande, equipe

    @staticmethod
    def accepter_demande(demande_id: int, capitaine_id: int) -> dict:
        """Accepte une demande : le joueur est ajouté à l'équipe."""
        try:
            with transaction() as conn:
                demande, equipe = DemandeService._demande_a_traiter(demande_id, capitaine_id, conn)

                tournoi = TournoiRepository.obtenir(conn, equipe["tournoi_id"])
                if tournoi and tournoi["statut"] != "OUVERT":
                    raise ValueError("Les inscriptions de ce tournoi sont closes")

                if demande["utilisateur_id"] not in equipe["joueurs_ids"]:
                    EquipeRepository.ajouter_membre(
                        conn, equipe["id"], demande["utilisateur_id"], equipe["tournoi_id"]
                    )

                return DemandeRepository.changer_statut(conn, demande_id, "ACCEPTEE")
        except sqlite3.IntegrityError as e:
            # ex. le joueur est déjà dans une autre équipe de ce tournoi
            raise erreur_metier(e) from e

    @staticmethod
    def refuser_demande(demande_id: int, capitaine_id: int) -> dict:
        """Refuse une demande."""
        with transaction() as conn:
            DemandeService._demande_a_traiter(demande_id, capitaine_id, conn)
            return DemandeRepository.changer_statut(conn, demande_id, "REFUSEE")
