import sqlite3
from typing import List, Optional

from backTournoi.main.repo.equipe_repository import EquipeRepository
from backTournoi.main.repo.match_repository import MatchRepository
from backTournoi.main.repo.message_repository import MessageRepository
from backTournoi.main.repo.tournoi_repository import TournoiRepository
from backTournoi.main.repo.utilisateur_repository import UtilisateurRepository
from backTournoi.main.utils.data.erreurs_sql import erreur_metier
from backTournoi.main.utils.data.transaction import transaction
from backTournoi.main.dto.equipe_dto import EquipeCreate


class EquipeService:
    """Contient toute la logique métier liée aux équipes."""

    @staticmethod
    def lister_equipes() -> List[dict]:
        """Retourne la liste brute de toutes les équipes."""
        with transaction() as conn:
            return EquipeRepository.lister(conn)

    @staticmethod
    def obtenir_equipe(equipe_id: int) -> Optional[dict]:
        """Retourne une équipe par son ID, sans enrichissement."""
        with transaction() as conn:
            return EquipeRepository.obtenir(conn, equipe_id)

    @staticmethod
    def peut_lire_messages(equipe: dict, utilisateur: Optional[dict]) -> bool:
        """Le chat d'équipe n'est lisible que par les membres de l'équipe et par
        les administrateurs. Un visiteur (utilisateur None) n'y a jamais accès."""
        if utilisateur is None:
            return False
        return bool(utilisateur.get("is_admin")) or utilisateur["id"] in equipe["joueurs_ids"]

    @staticmethod
    def obtenir_equipe_detail(equipe_id: int, inclure_messages: bool = True) -> Optional[dict]:
        """Retourne une équipe enrichie avec son tournoi, ses joueurs, ses matchs
        et (si inclure_messages) ses messages. Sans droit de lecture, `messages`
        vaut None. C'est au contrôleur de décider via peut_lire_messages."""
        with transaction() as conn:
            equipe = EquipeRepository.obtenir(conn, equipe_id)
            if not equipe:
                return None

            joueurs = [UtilisateurRepository.obtenir(conn, uid) for uid in equipe["joueurs_ids"]]
            tournoi = TournoiRepository.obtenir(conn, equipe["tournoi_id"])

            equipe_matchs = MatchRepository.lister_par_equipe(conn, equipe_id)
            equipe_messages = (
                MessageRepository.lister(conn, equipe_id)
                if inclure_messages
                else None
            )

        return {
            **equipe,
            "tournoi": tournoi,
            "joueurs": joueurs,
            "matchs": equipe_matchs,
            "messages": equipe_messages,
        }

    @staticmethod
    def creer_equipe(payload: EquipeCreate) -> dict:
        """Crée une nouvelle équipe et l'ajoute au tournoi correspondant.
        Le capitaine est le premier joueur de la liste. Si une règle n'est pas
        respectée (ValueError), aucune équipe n'est créée."""
        try:
            with transaction() as conn:
                if not TournoiRepository.obtenir(conn, payload.tournoi_id):
                    raise ValueError(f"Le tournoi {payload.tournoi_id} n'existe pas.")

                for uid in payload.joueurs_ids:
                    joueur = UtilisateurRepository.obtenir(conn, uid)
                    if joueur and joueur.get("is_admin"):
                        raise ValueError(
                            f"'{joueur['login']}' est administrateur : "
                            "un administrateur ne peut pas faire partie d'une équipe."
                        )

                if not payload.joueurs_ids:
                    raise ValueError("Une équipe doit avoir au moins un joueur (son capitaine).")

                # Les contraintes de la base (nom unique par tournoi, un joueur par
                # équipe et par tournoi, joueurs existants, doublons) sont vérifiées
                # à l'insertion / au COMMIT.
                return EquipeRepository.creer(
                    conn,
                    nom=payload.nom,
                    tournoi_id=payload.tournoi_id,
                    capitaine_id=payload.joueurs_ids[0],
                    joueurs_ids=payload.joueurs_ids,
                )
        except sqlite3.IntegrityError as e:
            raise erreur_metier(e) from e
