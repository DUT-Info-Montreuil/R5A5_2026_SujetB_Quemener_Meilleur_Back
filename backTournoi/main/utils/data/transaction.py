"""Gestionnaire de transaction SQLite pour le projet tournoi."""

from contextlib import contextmanager
import sqlite3
from typing import Iterator

from backTournoi.main.utils.data.database import get_connection


@contextmanager
def transaction() -> Iterator[sqlite3.Connection]:
    """Ouvre une connexion dans une transaction et la met à disposition.

    Le commit, le rollback et la fermeture de la connexion sont déjà gérés
    par get_connection() dans database.py. Il ne faut donc pas les répéter ici.

    Exemple :
        with transaction() as conn:
            conn.execute("INSERT INTO ...", (...))
    """
    with get_connection() as conn:
        yield conn
