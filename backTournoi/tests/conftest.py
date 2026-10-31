"""Base SQLite de test : isolée (fichier temporaire par test) et alimentée avec les
mêmes données que l'ancien data.py. La vraie base n'est jamais ouverte : la
fonction de connexion utilisée par `transaction()` est redirigée vers le fichier
temporaire."""
import os
import sqlite3
from pathlib import Path

import pytest

from backTournoi.main.utils.data import transaction as module_transaction


def _chemin_schema() -> Path:
    """Cherche schema.sql dans le dossier backTournoi (sans parcourir node_modules, etc.)."""
    for parent in Path(__file__).resolve().parents:
        racine = parent / "backTournoi"
        if racine.is_dir():
            for dossier, sous_dossiers, fichiers in os.walk(racine):
                sous_dossiers[:] = [d for d in sous_dossiers if d not in {"__pycache__", ".git", "venv", ".venv"}]
                if "schema.sql" in fichiers:
                    return Path(dossier) / "schema.sql"
    raise FileNotFoundError("schema.sql introuvable sous le dossier backTournoi")


SCHEMA_SQL = _chemin_schema()

# --- Données de départ (reprises de l'ancien data.py) ---------------------------
# Mot de passe en clair pour les comptes de test (non haché : évite le coût de bcrypt).
# alex n'est pas administrateur : l'ancien data.py utilisait la clé "isAdmin", jamais
# lue par la logique (seul Michel, avec "is_admin", était réellement admin).
# Les utilisateurs 17 à 20 n'appartiennent à aucune équipe (utile pour créer des
# équipes : un joueur ne peut être que dans une équipe par tournoi).
LOGINS = {
    1: "alex", 2: "max", 3: "lina", 4: "tom", 5: "sarah", 6: "nathan", 7: "emma",
    8: "lucas", 9: "chloe", 10: "hugo", 11: "lea", 12: "enzo", 13: "jade",
    14: "noah", 15: "zoe", 16: "yanis", 17: "libre1", 18: "libre2", 19: "libre3",
    20: "libre4", 67: "Michel",
}
ADMINS = {67}

TOURNOIS = [
    (1, "Summer Cup 2026", "Tournoi fictif de League of Legends", "FERME", 1),
    (2, "Autumn Cup 2026", "Tournoi fictif de Valorant", "TERMINE", 1),
]

# (id, nom, tournoi_id, joueurs) : le capitaine est le premier joueur.
EQUIPES = [
    (1, "Les Dragons", 1, [1, 2, 3, 4]),
    (2, "Les Tigres", 1, [5, 6, 7, 8]),
    (3, "Les Phoenix", 1, [9, 10, 11, 12]),
    (4, "Les Loups", 1, [13, 14, 15, 16]),
    (5, "Les Dragons", 2, [1, 5, 9, 13]),
    (6, "Les Tigres", 2, [2, 6, 10, 14]),
    (7, "Les Phoenix", 2, [3, 7, 11, 15]),
    (8, "Les Loups", 2, [4, 8, 12, 16]),
]

# (id, round, position, e1, e2, s1, s2, vainqueur, next, slot, loser_next, loser_slot, petite)
MATCHS_TOURNOI_2 = [
    (1, 1, 0, 5, 8, 2, 1, 5, 3, 1, 4, 1, 0),
    (2, 1, 1, 6, 7, 2, 0, 6, 3, 2, 4, 2, 0),
    (3, 2, 0, 5, 6, 3, 1, 5, None, None, None, None, 0),
    (4, 2, 1, 8, 7, 2, 0, 8, None, None, None, None, 1),
]

MESSAGES = [
    (1, 1, 1, "Bienvenue dans l'équipe !"),
    (2, 2, 5, "Bon tournoi à tous !"),
    (3, 3, 9, "On est prêts !"),
    (4, 4, 13, "Rendez-vous demain matin."),
    (5, 5, 1, "Bienvenue pour le deuxième tournoi !"),
]

DEMANDES = [
    (1, 2, 2, "EN_ATTENTE"),
    (2, 4, 3, "EN_ATTENTE"),
    (3, 3, 4, "REFUSEE"),
]


def _remplir(conn: sqlite3.Connection) -> None:
    conn.executemany(
        "INSERT INTO utilisateurs (id, login, mdp, is_admin) VALUES (?, ?, ?, ?)",
        [(i, login, "motdepasse_test", int(i in ADMINS)) for i, login in LOGINS.items()],
    )
    conn.executemany(
        "INSERT INTO tournois (id, nom, description, statut, petite_finale) VALUES (?, ?, ?, ?, ?)",
        TOURNOIS,
    )
    # equipes avant membres : la FK du capitaine est différée (vérifiée au COMMIT)
    for equipe_id, nom, tournoi_id, joueurs in EQUIPES:
        conn.execute(
            "INSERT INTO equipes (id, nom, tournoi_id, capitaine_id) VALUES (?, ?, ?, ?)",
            (equipe_id, nom, tournoi_id, joueurs[0]),
        )
        conn.executemany(
            "INSERT INTO membres (equipe_id, utilisateur_id, tournoi_id) VALUES (?, ?, ?)",
            [(equipe_id, j, tournoi_id) for j in joueurs],
        )
    conn.executemany(
        "INSERT INTO matchs (id, tournoi_id, round, position, equipe1_id, equipe2_id, "
        "score_equipe1, score_equipe2, vainqueur_id, next_match_id, next_slot, "
        "loser_next_match_id, loser_next_slot, petite_finale, bye) "
        "VALUES (?, 2, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)",
        MATCHS_TOURNOI_2,
    )
    conn.executemany(
        "INSERT INTO messages (id, equipe_id, utilisateur_id, message) VALUES (?, ?, ?, ?)",
        MESSAGES,
    )
    conn.executemany(
        "INSERT INTO demandes (id, equipe_id, utilisateur_id, statut) VALUES (?, ?, ?, ?)",
        DEMANDES,
    )


@pytest.fixture(autouse=True)
def base_de_test(tmp_path, monkeypatch):
    """Crée une base SQLite temporaire (schéma + données de départ) pour chaque test
    et redirige toutes les connexions de l'application vers elle. Remplace les anciennes
    fixtures `reinitialiser_donnees` (sauvegarde / restauration des listes de data.py)."""
    chemin = tmp_path / "test.db"

    def connexion_de_test() -> sqlite3.Connection:
        return sqlite3.connect(chemin)

    monkeypatch.setattr(module_transaction, "get_connection", connexion_de_test)

    conn = connexion_de_test()
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA_SQL.read_text(encoding="utf-8"))
        _remplir(conn)
        conn.commit()
    finally:
        conn.close()
    yield chemin
