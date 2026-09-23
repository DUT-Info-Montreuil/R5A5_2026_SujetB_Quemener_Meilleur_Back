# Importation de toutes tes données et fonctions d'accès depuis utils/data/data.py
from backTournoi.main.utils.data.data import (
    jeux,
    utilisateurs,
    equipes,
    tournois,
    matchs,
    messages,
    get_tournoi,
    get_equipe,
    get_utilisateur,
    get_jeu,
)


# ============================================================
# TESTS : CHARGEMENT ET VOLUMÉTRIE DES DONNÉES
# ============================================================

def test_chargement_donnees():
    """Vérifie le nombre total d'éléments dans chaque liste de données."""
    assert len(jeux) == 2
    assert len(utilisateurs) == 16
    assert len(equipes) == 8
    assert len(tournois) == 2
    assert len(matchs) == 12
    assert len(messages) == 5


# ============================================================
# TESTS : FONCTION GET_JEU
# ============================================================

def test_get_jeu_existant():
    """Vérifie la recherche d'un jeu par son ID."""
    jeu = get_jeu(1)
    assert jeu is not None
    assert jeu["nom"] == "League of Legends"


def test_get_jeu_inexistant():
    """Vérifie qu'un ID de jeu inconnu renvoie None."""
    assert get_jeu(999) is None


# ============================================================
# TESTS : FONCTION GET_UTILISATEUR ET RÔLES
# ============================================================

def test_get_utilisateur_admin():
    """Vérifie les données de l'administrateur (Alex)."""
    alex = get_utilisateur(1)
    assert alex is not None
    assert alex["login"] == "alex"
    assert alex["isAdmin"] is True


def test_get_utilisateur_classique():
    """Vérifie les données d'un utilisateur standard."""
    user = get_utilisateur(2)
    assert user is not None
    assert user["login"] == "max"
    assert user.get("isAdmin") is not True


# ============================================================
# TESTS : FONCTION GET_TOURNOI ET RELATIONS
# ============================================================

def test_get_tournoi_existant():
    """Vérifie la récupération des infos d'un tournoi."""
    tournoi = get_tournoi(1)
    assert tournoi is not None
    assert tournoi["nom"] == "Summer Cup 2026"
    assert tournoi["jeu_id"] == 1
    assert len(tournoi["equipes_ids"]) == 4


def test_get_tournoi_inexistant():
    """Vérifie qu'un ID de tournoi inconnu renvoie None."""
    assert get_tournoi(999) is None


# ============================================================
# TESTS : FONCTION GET_EQUIPE ET MAPPING JOUEURS
# ============================================================

def test_get_equipe_existant():
    """Vérifie la récupération d'une équipe et la cohérence de ses joueurs."""
    equipe = get_equipe(1)
    assert equipe is not None
    assert equipe["nom"] == "Les Dragons"
    assert equipe["tournoi_id"] == 1
    assert len(equipe["joueurs_ids"]) == 4

    # Vérification que tous les joueurs de l'équipe existent bien dans la liste utilisateurs
    for joueur_id in equipe["joueurs_ids"]:
        joueur = get_utilisateur(joueur_id)
        assert joueur is not None


def test_get_equipe_inexistant():
    """Vérifie qu'un ID d'équipe inconnu renvoie None."""
    assert get_equipe(999) is None


# ============================================================
# TESTS : COHÉRENCE DES MATCHS ET MESSAGES
# ============================================================

def test_coherence_matchs_tournoi():
    """Vérifie que les matchs sont correctement répartis entre les tournois."""
    # Filtrage des matchs du tournoi 1 (équipes 1 à 4)
    matchs_tournoi_1 = [m for m in matchs if m["equipe1_id"] in [1, 2, 3, 4]]
    assert len(matchs_tournoi_1) == 6

    # Filtrage des matchs du tournoi 2 (équipes 5 à 8)
    matchs_tournoi_2 = [m for m in matchs if m["equipe1_id"] in [5, 6, 7, 8]]
    assert len(matchs_tournoi_2) == 6


def test_coherence_messages_equipe():
    """Vérifie les messages rattachés à une équipe."""
    messages_equipe_1 = [m for m in messages if m["equipe_id"] == 1]
    assert len(messages_equipe_1) == 1
    assert messages_equipe_1[0]["message"] == "Bienvenue dans l'équipe !"


# ============================================================
# 3. BLOC D'EXÉCUTION EN BAS DU FICHIER (Pour lancer le rapport)
# ============================================================
if __name__ == "__main__":
    import pytest
    pytest.main(["-v", __file__])