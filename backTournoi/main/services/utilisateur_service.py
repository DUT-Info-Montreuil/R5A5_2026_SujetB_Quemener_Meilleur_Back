import sqlite3
from typing import List, Optional

from backTournoi.main.repo.equipe_repository import EquipeRepository
from backTournoi.main.repo.message_repository import MessageRepository
from backTournoi.main.repo.utilisateur_repository import UtilisateurRepository
from backTournoi.main.utils.data.erreurs_sql import erreur_metier
from backTournoi.main.utils.data.transaction import transaction
from backTournoi.main.utils.security import hash_password
from backTournoi.main.dto.utilisateur_dto import UtilisateurCreate, UtilisateurUpdate

# Champs qui ne peuvent pas être mis à null lors d'un PATCH
CHAMPS_NON_NULLABLES = ("login", "mdp", "is_admin")


class UtilisateurService:
    """Contient toute la logique métier liée aux utilisateurs."""

    @staticmethod
    def lister_utilisateurs() -> List[dict]:
        """Retourne la liste brute de tous les utilisateurs."""
        with transaction() as conn:
            return UtilisateurRepository.lister(conn)

    @staticmethod
    def obtenir_utilisateur(utilisateur_id: int) -> Optional[dict]:
        """Retourne un utilisateur par son ID, sans enrichissement."""
        with transaction() as conn:
            return UtilisateurRepository.obtenir(conn, utilisateur_id)

    @staticmethod
    def obtenir_utilisateur_detail(utilisateur_id: int) -> Optional[dict]:
        """Retourne un utilisateur enrichi avec ses équipes et ses messages."""
        with transaction() as conn:
            utilisateur = UtilisateurRepository.obtenir(conn, utilisateur_id)
            if not utilisateur:
                return None

            utilisateur_equipes = EquipeRepository.lister_par_utilisateur(conn, utilisateur_id)
            utilisateur_messages = MessageRepository.lister_par_utilisateur(conn, utilisateur_id)

        return {
            **utilisateur,
            "equipes": utilisateur_equipes,
            "messages": utilisateur_messages,
        }

    @staticmethod
    def creer_utilisateur(payload: UtilisateurCreate) -> dict:
        """Crée un nouvel utilisateur. Le login doit être unique.
        Le mot de passe est stocké haché (bcrypt)."""
        mdp_hache = hash_password(payload.mdp)
        try:
            with transaction() as conn:
                if UtilisateurRepository.obtenir_par_login(conn, payload.login):
                    raise ValueError(f"Le login '{payload.login}' existe déjà.")

                return UtilisateurRepository.creer(
                    conn, payload.login, mdp_hache, payload.is_admin
                )
        except sqlite3.IntegrityError as e:
            raise erreur_metier(e) from e

    @staticmethod
    def modifier_utilisateur(
        utilisateur_id: int, payload: UtilisateurUpdate
    ) -> Optional[dict]:
        """Modifie les champs fournis d'un utilisateur (PATCH).
        Renvoie None si l'utilisateur n'existe pas."""
        try:
            with transaction() as conn:
                utilisateur = UtilisateurRepository.obtenir(conn, utilisateur_id)
                if not utilisateur:
                    return None

                modifications = payload.model_dump(exclude_unset=True)

                # Toutes les vérifications se font avant la moindre modification
                for champ in CHAMPS_NON_NULLABLES:
                    if champ in modifications and modifications[champ] is None:
                        raise ValueError(f"Le champ '{champ}' ne peut pas être null.")

                if "login" in modifications:
                    autre = UtilisateurRepository.obtenir_par_login(conn, modifications["login"])
                    if autre and autre["id"] != utilisateur_id:
                        raise ValueError(f"Le login '{modifications['login']}' existe déjà.")

                if "mdp" in modifications:
                    modifications["mdp"] = hash_password(modifications["mdp"])

                return UtilisateurRepository.modifier(conn, utilisateur_id, modifications)
        except sqlite3.IntegrityError as e:
            raise erreur_metier(e) from e
