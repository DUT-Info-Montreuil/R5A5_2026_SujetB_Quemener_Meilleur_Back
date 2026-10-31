from typing import List, Optional

from backTournoi.main.repo._base import tous, un

_SELECT = "SELECT id, nom, tournoi_id, capitaine_id FROM equipes"


def _avec_joueurs(conn, equipes: List[dict]) -> List[dict]:
    """Ajoute `joueurs_ids` (ordre d'insertion dans `membres`) à chaque équipe."""
    if not equipes:
        return equipes
    ids = [e["id"] for e in equipes]
    marques = ",".join("?" * len(ids))
    joueurs: dict = {}
    for equipe_id, utilisateur_id in conn.execute(
        f"SELECT equipe_id, utilisateur_id FROM membres "
        f"WHERE equipe_id IN ({marques}) ORDER BY rowid",
        ids,
    ).fetchall():
        joueurs.setdefault(equipe_id, []).append(utilisateur_id)
    for e in equipes:
        e["joueurs_ids"] = joueurs.get(e["id"], [])
    return equipes


class EquipeRepository:
    """Requêtes SQL des tables `equipes` et `membres` (aucune logique métier).
    `joueurs_ids` est reconstruit depuis `membres`, `capitaine_id` vient de `equipes`."""

    @staticmethod
    def lister(conn) -> List[dict]:
        return _avec_joueurs(conn, tous(conn.execute(f"{_SELECT} ORDER BY id")))

    @staticmethod
    def lister_par_tournoi(conn, tournoi_id: int) -> List[dict]:
        return _avec_joueurs(
            conn, tous(conn.execute(f"{_SELECT} WHERE tournoi_id = ? ORDER BY id", (tournoi_id,)))
        )

    @staticmethod
    def lister_par_utilisateur(conn, utilisateur_id: int) -> List[dict]:
        return _avec_joueurs(
            conn,
            tous(
                conn.execute(
                    "SELECT e.id, e.nom, e.tournoi_id, e.capitaine_id FROM equipes e "
                    "JOIN membres m ON m.equipe_id = e.id "
                    "WHERE m.utilisateur_id = ? ORDER BY e.id",
                    (utilisateur_id,),
                )
            ),
        )

    @staticmethod
    def obtenir(conn, equipe_id: int) -> Optional[dict]:
        equipe = un(conn.execute(f"{_SELECT} WHERE id = ?", (equipe_id,)))
        if equipe is None:
            return None
        return _avec_joueurs(conn, [equipe])[0]

    @staticmethod
    def creer(conn, nom: str, tournoi_id: int, capitaine_id: int, joueurs_ids: List[int]) -> dict:
        """Insère l'équipe puis ses membres. Le capitaine doit figurer dans
        `joueurs_ids` (contrainte vérifiée par la base au COMMIT)."""
        curseur = conn.execute(
            "INSERT INTO equipes (nom, tournoi_id, capitaine_id) VALUES (?, ?, ?)",
            (nom, tournoi_id, capitaine_id),
        )
        equipe_id = curseur.lastrowid
        for utilisateur_id in joueurs_ids:
            EquipeRepository.ajouter_membre(conn, equipe_id, utilisateur_id, tournoi_id)
        return EquipeRepository.obtenir(conn, equipe_id)

    @staticmethod
    def ajouter_membre(conn, equipe_id: int, utilisateur_id: int, tournoi_id: int) -> None:
        conn.execute(
            "INSERT INTO membres (equipe_id, utilisateur_id, tournoi_id) VALUES (?, ?, ?)",
            (equipe_id, utilisateur_id, tournoi_id),
        )
