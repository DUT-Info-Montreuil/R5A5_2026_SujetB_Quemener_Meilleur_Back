from typing import List, Optional

from backTournoi.main.repo._base import tous, un

COLONNES = (
    "id", "tournoi_id", "round", "position", "equipe1_id", "equipe2_id",
    "score_equipe1", "score_equipe2", "vainqueur_id", "next_match_id", "next_slot",
    "loser_next_match_id", "loser_next_slot", "petite_finale", "bye",
)
_SELECT = f"SELECT {', '.join(COLONNES)} FROM matchs"
_COLONNE_EQUIPE = {1: "equipe1_id", 2: "equipe2_id"}


def _formater(match: Optional[dict]) -> Optional[dict]:
    if match is not None:
        match["petite_finale"] = bool(match["petite_finale"])
        match["bye"] = bool(match["bye"])
    return match


class MatchRepository:
    """Requêtes SQL de la table `matchs` (aucune logique métier)."""

    @staticmethod
    def lister(conn) -> List[dict]:
        return [_formater(m) for m in tous(conn.execute(f"{_SELECT} ORDER BY id"))]

    @staticmethod
    def obtenir(conn, match_id: int) -> Optional[dict]:
        return _formater(un(conn.execute(f"{_SELECT} WHERE id = ?", (match_id,))))

    @staticmethod
    def lister_par_tournoi(conn, tournoi_id: int) -> List[dict]:
        return [
            _formater(m)
            for m in tous(conn.execute(f"{_SELECT} WHERE tournoi_id = ? ORDER BY id", (tournoi_id,)))
        ]

    @staticmethod
    def lister_par_equipe(conn, equipe_id: int) -> List[dict]:
        return [
            _formater(m)
            for m in tous(
                conn.execute(
                    f"{_SELECT} WHERE equipe1_id = ? OR equipe2_id = ? ORDER BY id",
                    (equipe_id, equipe_id),
                )
            )
        ]

    @staticmethod
    def existe_pour_tournoi(conn, tournoi_id: int) -> bool:
        return conn.execute(
            "SELECT 1 FROM matchs WHERE tournoi_id = ? LIMIT 1", (tournoi_id,)
        ).fetchone() is not None

    @staticmethod
    def prochain_id(conn) -> int:
        return conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM matchs").fetchone()[0]

    @staticmethod
    def inserer_plusieurs(conn, matchs: List[dict]) -> None:
        """Insère des matchs complets (les clés vers d'autres matchs sont des clés
        étrangères différées : l'ordre d'insertion n'a pas d'importance)."""
        conn.executemany(
            f"INSERT INTO matchs ({', '.join(COLONNES)}) "
            f"VALUES ({', '.join(':' + c for c in COLONNES)})",
            [
                {**m, "petite_finale": int(bool(m["petite_finale"])), "bye": int(bool(m["bye"]))}
                for m in matchs
            ],
        )

    @staticmethod
    def enregistrer_resultat(conn, match_id: int, score1: int, score2: int, vainqueur_id: int) -> None:
        conn.execute(
            "UPDATE matchs SET score_equipe1 = ?, score_equipe2 = ?, vainqueur_id = ? WHERE id = ?",
            (score1, score2, vainqueur_id, match_id),
        )

    @staticmethod
    def placer_equipe(conn, match_id: int, slot: int, equipe_id: int) -> None:
        """Place une équipe dans l'emplacement 1 ou 2 d'un match."""
        colonne = _COLONNE_EQUIPE[slot]
        conn.execute(f"UPDATE matchs SET {colonne} = ? WHERE id = ?", (equipe_id, match_id))
