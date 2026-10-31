from typing import List, Optional

from backTournoi.main.repo._base import tous, un

COLONNES_MODIFIABLES = ("nom", "description", "statut", "petite_finale")
_SELECT = "SELECT id, nom, description, statut, petite_finale FROM tournois"


def _formater(tournoi: dict, equipes_ids: List[int]) -> dict:
    tournoi["petite_finale"] = bool(tournoi["petite_finale"])
    tournoi["equipes_ids"] = equipes_ids
    return tournoi


class TournoiRepository:
    """Requêtes SQL de la table `tournois`. `equipes_ids` est reconstruit à partir
    de `equipes.tournoi_id` (aucune logique métier)."""

    @staticmethod
    def lister(conn) -> List[dict]:
        equipes_par_tournoi: dict = {}
        for tournoi_id, equipe_id in conn.execute(
            "SELECT tournoi_id, id FROM equipes ORDER BY id"
        ).fetchall():
            equipes_par_tournoi.setdefault(tournoi_id, []).append(equipe_id)
        return [
            _formater(t, equipes_par_tournoi.get(t["id"], []))
            for t in tous(conn.execute(f"{_SELECT} ORDER BY id"))
        ]

    @staticmethod
    def obtenir(conn, tournoi_id: int) -> Optional[dict]:
        tournoi = un(conn.execute(f"{_SELECT} WHERE id = ?", (tournoi_id,)))
        if tournoi is None:
            return None
        equipes_ids = [
            ligne[0]
            for ligne in conn.execute(
                "SELECT id FROM equipes WHERE tournoi_id = ? ORDER BY id", (tournoi_id,)
            ).fetchall()
        ]
        return _formater(tournoi, equipes_ids)

    @staticmethod
    def creer(conn, nom: str, description: Optional[str], petite_finale: bool, statut: str) -> dict:
        curseur = conn.execute(
            "INSERT INTO tournois (nom, description, statut, petite_finale) VALUES (?, ?, ?, ?)",
            (nom, description, statut, int(bool(petite_finale))),
        )
        return TournoiRepository.obtenir(conn, curseur.lastrowid)

    @staticmethod
    def modifier(conn, tournoi_id: int, modifications: dict) -> Optional[dict]:
        """Met à jour les colonnes fournies (liste blanche) et renvoie le tournoi."""
        colonnes = [c for c in COLONNES_MODIFIABLES if c in modifications]
        if colonnes:
            valeurs = [
                int(bool(modifications[c])) if c == "petite_finale" else modifications[c]
                for c in colonnes
            ]
            conn.execute(
                f"UPDATE tournois SET {', '.join(c + ' = ?' for c in colonnes)} WHERE id = ?",
                (*valeurs, tournoi_id),
            )
        return TournoiRepository.obtenir(conn, tournoi_id)
