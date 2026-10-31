from typing import List, Optional

from backTournoi.main.repo._base import tous, un

_SELECT = "SELECT id, equipe_id, utilisateur_id, statut FROM demandes"


class DemandeRepository:
    """Requêtes SQL de la table `demandes` (aucune logique métier)."""

    @staticmethod
    def lister(conn, equipe_id: Optional[int] = None) -> List[dict]:
        if equipe_id is None:
            return tous(conn.execute(f"{_SELECT} ORDER BY id"))
        return tous(conn.execute(f"{_SELECT} WHERE equipe_id = ? ORDER BY id", (equipe_id,)))

    @staticmethod
    def obtenir(conn, demande_id: int) -> Optional[dict]:
        return un(conn.execute(f"{_SELECT} WHERE id = ?", (demande_id,)))

    @staticmethod
    def existe_en_attente(conn, equipe_id: int, utilisateur_id: int) -> bool:
        return conn.execute(
            "SELECT 1 FROM demandes WHERE equipe_id = ? AND utilisateur_id = ? "
            "AND statut = 'EN_ATTENTE' LIMIT 1",
            (equipe_id, utilisateur_id),
        ).fetchone() is not None

    @staticmethod
    def creer(conn, equipe_id: int, utilisateur_id: int, statut: str) -> dict:
        curseur = conn.execute(
            "INSERT INTO demandes (equipe_id, utilisateur_id, statut) VALUES (?, ?, ?)",
            (equipe_id, utilisateur_id, statut),
        )
        return DemandeRepository.obtenir(conn, curseur.lastrowid)

    @staticmethod
    def changer_statut(conn, demande_id: int, statut: str) -> Optional[dict]:
        conn.execute("UPDATE demandes SET statut = ? WHERE id = ?", (statut, demande_id))
        return DemandeRepository.obtenir(conn, demande_id)
