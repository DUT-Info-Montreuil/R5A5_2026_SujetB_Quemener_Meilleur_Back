from typing import List, Optional

from backTournoi.main.repo._base import tous, un

COLONNES_MODIFIABLES = ("login", "mdp", "is_admin")
_SELECT = "SELECT id, login, mdp, is_admin FROM utilisateurs"


def _formater(utilisateur: Optional[dict]) -> Optional[dict]:
    if utilisateur is not None:
        utilisateur["is_admin"] = bool(utilisateur["is_admin"])
    return utilisateur


class UtilisateurRepository:
    """Requêtes SQL de la table `utilisateurs` (aucune logique métier)."""

    @staticmethod
    def lister(conn) -> List[dict]:
        return [_formater(u) for u in tous(conn.execute(f"{_SELECT} ORDER BY id"))]

    @staticmethod
    def obtenir(conn, utilisateur_id: int) -> Optional[dict]:
        return _formater(un(conn.execute(f"{_SELECT} WHERE id = ?", (utilisateur_id,))))

    @staticmethod
    def obtenir_par_login(conn, login: str) -> Optional[dict]:
        return _formater(un(conn.execute(f"{_SELECT} WHERE login = ?", (login,))))

    @staticmethod
    def creer(conn, login: str, mdp: str, is_admin: bool) -> dict:
        curseur = conn.execute(
            "INSERT INTO utilisateurs (login, mdp, is_admin) VALUES (?, ?, ?)",
            (login, mdp, int(bool(is_admin))),
        )
        return UtilisateurRepository.obtenir(conn, curseur.lastrowid)

    @staticmethod
    def modifier(conn, utilisateur_id: int, modifications: dict) -> Optional[dict]:
        """Met à jour les colonnes fournies (liste blanche) et renvoie l'utilisateur."""
        colonnes = [c for c in COLONNES_MODIFIABLES if c in modifications]
        if colonnes:
            valeurs = [
                int(bool(modifications[c])) if c == "is_admin" else modifications[c]
                for c in colonnes
            ]
            conn.execute(
                f"UPDATE utilisateurs SET {', '.join(c + ' = ?' for c in colonnes)} WHERE id = ?",
                (*valeurs, utilisateur_id),
            )
        return UtilisateurRepository.obtenir(conn, utilisateur_id)
