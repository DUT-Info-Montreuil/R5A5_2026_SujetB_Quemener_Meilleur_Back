from typing import List, Optional

from backTournoi.main.utils.data.data import (
    utilisateurs,
    equipes,
    messages,
    get_utilisateur,
)
from backTournoi.main.dto.utilisateur_dto import UtilisateurCreate, UtilisateurUpdate

# Champs qui ne peuvent pas être mis à null lors d'un PATCH
CHAMPS_NON_NULLABLES = ("login", "mdp", "is_admin")


class UtilisateurService:
    """Contient toute la logique métier liée aux utilisateurs."""

    @staticmethod
    def lister_utilisateurs() -> List[dict]:
        """Retourne la liste brute de tous les utilisateurs."""
        return utilisateurs

    @staticmethod
    def obtenir_utilisateur(utilisateur_id: int) -> Optional[dict]:
        """Retourne un utilisateur par son ID, sans enrichissement."""
        return get_utilisateur(utilisateur_id)

    @staticmethod
    def obtenir_utilisateur_detail(utilisateur_id: int) -> Optional[dict]:
        """Retourne un utilisateur enrichi avec ses équipes et ses messages."""
        utilisateur = get_utilisateur(utilisateur_id)
        if not utilisateur:
            return None

        utilisateur_equipes = [
            e for e in equipes if utilisateur_id in e["joueurs_ids"]
        ]
        utilisateur_messages = [
            m for m in messages if m["utilisateur_id"] == utilisateur_id
        ]

        return {
            **utilisateur,
            "equipes": utilisateur_equipes,
            "messages": utilisateur_messages,
        }

    @staticmethod
    def creer_utilisateur(payload: UtilisateurCreate) -> dict:
        """Crée un nouvel utilisateur. Le login doit être unique."""
        if any(u["login"] == payload.login for u in utilisateurs):
            raise ValueError(f"Le login '{payload.login}' existe déjà.")

        nouvel_id = max((u["id"] for u in utilisateurs), default=0) + 1

        nouvel_utilisateur = {
            "id": nouvel_id,
            "login": payload.login,
            "mdp": payload.mdp,
            "is_admin": payload.is_admin,
        }

        utilisateurs.append(nouvel_utilisateur)
        return nouvel_utilisateur

    @staticmethod
    def modifier_utilisateur(
        utilisateur_id: int, payload: UtilisateurUpdate
    ) -> Optional[dict]:
        """Modifie les champs fournis d'un utilisateur (PATCH).
        Renvoie None si l'utilisateur n'existe pas."""
        utilisateur = get_utilisateur(utilisateur_id)
        if not utilisateur:
            return None

        modifications = payload.model_dump(exclude_unset=True)

        # Toutes les vérifications se font avant la moindre modification
        for champ in CHAMPS_NON_NULLABLES:
            if champ in modifications and modifications[champ] is None:
                raise ValueError(f"Le champ '{champ}' ne peut pas être null.")

        if "login" in modifications and any(
            u["login"] == modifications["login"] and u["id"] != utilisateur_id
            for u in utilisateurs
        ):
            raise ValueError(f"Le login '{modifications['login']}' existe déjà.")

        utilisateur.update(modifications)
        return utilisateur
