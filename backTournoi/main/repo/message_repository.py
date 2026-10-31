from typing import List, Optional

from backTournoi.main.repo._base import tous, un

_SELECT = "SELECT id, equipe_id, utilisateur_id, message FROM messages"


class MessageRepository:
    """Requêtes SQL de la table `messages` (aucune logique métier)."""

    @staticmethod
    def lister(conn, equipe_id: Optional[int] = None) -> List[dict]:
        if equipe_id is None:
            return tous(conn.execute(f"{_SELECT} ORDER BY id"))
        return tous(conn.execute(f"{_SELECT} WHERE equipe_id = ? ORDER BY id", (equipe_id,)))

    @staticmethod
    def lister_par_utilisateur(conn, utilisateur_id: int) -> List[dict]:
        return tous(conn.execute(f"{_SELECT} WHERE utilisateur_id = ? ORDER BY id", (utilisateur_id,)))

    @staticmethod
    def obtenir(conn, message_id: int) -> Optional[dict]:
        return un(conn.execute(f"{_SELECT} WHERE id = ?", (message_id,)))

    @staticmethod
    def creer(conn, equipe_id: int, utilisateur_id: int, message: str) -> dict:
        curseur = conn.execute(
            "INSERT INTO messages (equipe_id, utilisateur_id, message) VALUES (?, ?, ?)",
            (equipe_id, utilisateur_id, message),
        )
        return MessageRepository.obtenir(conn, curseur.lastrowid)
