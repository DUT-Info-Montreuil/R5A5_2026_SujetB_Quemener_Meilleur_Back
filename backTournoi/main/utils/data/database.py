"""Connexion SQLite (module natif `sqlite3`, sans ORM) et création du schéma."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

_DOSSIER = Path(__file__).resolve().parent

# Chemin calculé depuis ce fichier : ne dépend pas du dossier de lancement.
DB_PATH = _DOSSIER / "tournoi.db"
SCHEMA_PATH = _DOSSIER / "schema.sql"


def _ouvrir() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row  # accès aux colonnes par nom, dict(row) possible
    # Les clés étrangères sont désactivées par défaut : à réactiver à CHAQUE connexion.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Une connexion par opération, une transaction par bloc `with`.

    COMMIT à la sortie normale (c'est là que sont vérifiées les FK différées :
    capitaine membre de l'équipe, chaînage de l'arbre), ROLLBACK si une exception
    survient, puis fermeture dans tous les cas.

        with get_connection() as conn:
            conn.execute("INSERT INTO ...", (...))
    """
    conn = _ouvrir()
    try:
        yield conn
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Crée le fichier .db et toutes les tables/index s'ils n'existent pas.
    Sans danger à chaque démarrage (IF NOT EXISTS). Aucune donnée n'est insérée."""
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn = _ouvrir()
    try:
        conn.executescript(schema)
    finally:
        conn.close()
