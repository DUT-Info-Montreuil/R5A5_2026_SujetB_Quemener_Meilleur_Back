import copy

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

# Importation des données et fonctions d'accès depuis utils/data/data.py
from backTournoi.main.utils.data.data import (
    equipes,
    tournois,
    matchs,
    messages,
    get_equipe,
    get_tournoi,
    get_utilisateur,
)
from backTournoi.main.controllers.equipe_controller import (
    get_equipes,
    post_equipe,
    get_equipe_detail,
)
from backTournoi.main.services.equipe_service import EquipeService
from backTournoi.main.dto.equipe_dto import EquipeCreate


@pytest.fixture(autouse=True)
def reinitialiser_donnees():
    """Sauvegarde les listes des équipes et des tournois avant chaque test et les
    restaure après, pour que les tests de création n'influencent pas les autres
    (la création d'une équipe modifie aussi la liste equipes_ids du tournoi)."""
    sauvegarde_equipes = copy.deepcopy(equipes)
    sauvegarde_tournois = copy.deepcopy(tournois)
    yield
    equipes[:] = sauvegarde_equipes
    tournois[:] = sauvegarde_tournois


# ============================================================
# TESTS : SERVICE - LISTER_EQUIPES
# ============================================================

def test_lister_equipes_non_vide():
    """Vérifie que le service renvoie bien la liste des équipes des données factices."""
    resultat = EquipeService.lister_equipes()
    assert len(resultat) > 0
    assert resultat is equipes


def test_lister_equipes_structure():
    """Vérifie que chaque équipe contient les champs attendus."""
    champs = {"id", "nom", "tournoi_id", "joueurs_ids"}
    for equipe in EquipeService.lister_equipes():
        assert champs.issubset(equipe.keys())


def test_lister_equipes_ids_uniques():
    """Vérifie qu'il n'y a pas deux équipes avec le même ID."""
    ids = [e["id"] for e in EquipeService.lister_equipes()]
    assert len(ids) == len(set(ids))


def test_lister_equipes_tournoi_existant():
    """Vérifie que le tournoi de chaque équipe existe bien."""
    for equipe in EquipeService.lister_equipes():
        assert get_tournoi(equipe["tournoi_id"]) is not None


def test_lister_equipes_joueurs_existants():
    """Vérifie que tous les joueurs de chaque équipe existent bien."""
    for equipe in EquipeService.lister_equipes():
        for joueur_id in equipe["joueurs_ids"]:
            assert get_utilisateur(joueur_id) is not None


# ============================================================
# TESTS : SERVICE - OBTENIR_EQUIPE
# ============================================================

def test_obtenir_equipe():
    """Vérifie qu'une équipe existante est renvoyée par son ID."""
    attendue = equipes[0]
    equipe = EquipeService.obtenir_equipe(attendue["id"])
    assert equipe == attendue


def test_obtenir_equipe_sans_enrichissement():
    """Vérifie que l'équipe simple ne contient pas les champs enrichis."""
    equipe = EquipeService.obtenir_equipe(equipes[0]["id"])
    for champ in ("tournoi", "joueurs", "matchs", "messages"):
        assert champ not in equipe


def test_obtenir_equipe_inexistante():
    """Vérifie qu'un ID d'équipe inconnu renvoie None."""
    assert EquipeService.obtenir_equipe(999) is None


# ============================================================
# TESTS : SERVICE - OBTENIR_EQUIPE_DETAIL
# ============================================================

def test_obtenir_equipe_detail_champs():
    """Vérifie que le détail contient les champs de base et les champs enrichis."""
    detail = EquipeService.obtenir_equipe_detail(equipes[0]["id"])
    champs = {"id", "nom", "tournoi_id", "joueurs_ids",
              "tournoi", "joueurs", "matchs", "messages"}
    assert champs.issubset(detail.keys())


def test_obtenir_equipe_detail_tournoi():
    """Vérifie que le tournoi de l'équipe est bien joint au détail."""
    equipe = equipes[0]
    detail = EquipeService.obtenir_equipe_detail(equipe["id"])
    assert detail["tournoi"] == get_tournoi(equipe["tournoi_id"])


def test_obtenir_equipe_detail_joueurs():
    """Vérifie que les joueurs sont joints dans l'ordre de joueurs_ids."""
    equipe = equipes[0]
    detail = EquipeService.obtenir_equipe_detail(equipe["id"])
    assert len(detail["joueurs"]) == len(equipe["joueurs_ids"])
    assert [j["id"] for j in detail["joueurs"]] == equipe["joueurs_ids"]


def test_obtenir_equipe_detail_matchs():
    """Vérifie que seuls les matchs où l'équipe joue sont renvoyés."""
    equipe_id = equipes[0]["id"]
    detail = EquipeService.obtenir_equipe_detail(equipe_id)

    attendus = [m for m in matchs
                if m["equipe1_id"] == equipe_id or m["equipe2_id"] == equipe_id]
    assert detail["matchs"] == attendus
    for match in detail["matchs"]:
        assert equipe_id in (match["equipe1_id"], match["equipe2_id"])


def test_obtenir_equipe_detail_messages():
    """Vérifie que seuls les messages de l'équipe sont renvoyés."""
    equipe_id = equipes[0]["id"]
    detail = EquipeService.obtenir_equipe_detail(equipe_id)

    attendus = [m for m in messages if m["equipe_id"] == equipe_id]
    assert detail["messages"] == attendus
    for message in detail["messages"]:
        assert message["equipe_id"] == equipe_id


def test_obtenir_equipe_detail_ne_modifie_pas_les_donnees():
    """Vérifie que l'enrichissement n'ajoute rien à l'équipe stockée."""
    equipe_id = equipes[0]["id"]
    EquipeService.obtenir_equipe_detail(equipe_id)
    assert "matchs" not in get_equipe(equipe_id)
    assert "messages" not in get_equipe(equipe_id)


def test_obtenir_equipe_detail_inexistante():
    """Vérifie qu'un ID d'équipe inconnu renvoie None."""
    assert EquipeService.obtenir_equipe_detail(999) is None


# ============================================================
# TESTS : SERVICE - CREER_EQUIPE
# ============================================================

def test_creer_equipe():
    """Vérifie la création d'une équipe avec tous les champs."""
    nouvel_id = max(e["id"] for e in equipes) + 1
    tournoi_id = equipes[0]["tournoi_id"]
    payload = EquipeCreate(nom="Les Faucons", tournoi_id=tournoi_id, joueurs_ids=[1, 2])

    equipe = EquipeService.creer_equipe(payload)

    assert equipe["id"] == nouvel_id
    assert equipe["nom"] == "Les Faucons"
    assert equipe["tournoi_id"] == tournoi_id
    assert equipe["joueurs_ids"] == [1, 2]


def test_creer_equipe_ajoute_a_la_liste():
    """Vérifie que l'équipe créée est bien ajoutée à la liste des équipes."""
    avant = len(equipes)
    EquipeService.creer_equipe(EquipeCreate(nom="Les Faucons", tournoi_id=equipes[0]["tournoi_id"]))
    assert len(equipes) == avant + 1


def test_creer_equipe_ajoutee_au_tournoi():
    """Vérifie que l'ID de la nouvelle équipe est ajouté au tournoi concerné."""
    tournoi_id = equipes[0]["tournoi_id"]
    avant = len(get_tournoi(tournoi_id)["equipes_ids"])

    equipe = EquipeService.creer_equipe(EquipeCreate(nom="Les Faucons", tournoi_id=tournoi_id))

    tournoi = get_tournoi(tournoi_id)
    assert len(tournoi["equipes_ids"]) == avant + 1
    assert equipe["id"] in tournoi["equipes_ids"]


def test_creer_equipe_joueurs_par_defaut():
    """Vérifie que la liste de joueurs est vide quand elle n'est pas fournie."""
    equipe = EquipeService.creer_equipe(
        EquipeCreate(nom="Les Faucons", tournoi_id=equipes[0]["tournoi_id"])
    )
    assert equipe["joueurs_ids"] == []


def test_creer_equipe_ids_uniques():
    """Vérifie que deux créations successives reçoivent des ID différents."""
    tournoi_id = equipes[0]["tournoi_id"]
    e1 = EquipeService.creer_equipe(EquipeCreate(nom="Équipe A", tournoi_id=tournoi_id))
    e2 = EquipeService.creer_equipe(EquipeCreate(nom="Équipe B", tournoi_id=tournoi_id))
    assert e1["id"] != e2["id"]


def test_creer_equipe_tournoi_inexistant():
    """Vérifie qu'une équipe rattachée à un tournoi inconnu est refusée."""
    avant = len(equipes)
    with pytest.raises(ValueError, match="999"):
        EquipeService.creer_equipe(EquipeCreate(nom="Fantômes", tournoi_id=999))
    assert len(equipes) == avant


def test_creer_equipe_nom_vide():
    """Vérifie qu'un nom vide est rejeté par le DTO."""
    with pytest.raises(ValidationError):
        EquipeCreate(nom="", tournoi_id=1)


def test_creer_equipe_tournoi_manquant():
    """Vérifie qu'un payload sans tournoi_id est rejeté par le DTO."""
    with pytest.raises(ValidationError):
        EquipeCreate(nom="Les Faucons")


def test_creer_equipe_joueurs_invalides():
    """Vérifie qu'une liste de joueurs qui ne contient pas des entiers est rejetée."""
    with pytest.raises(ValidationError):
        EquipeCreate(nom="Les Faucons", tournoi_id=1, joueurs_ids=["alice"])


# ============================================================
# TESTS : CONTRÔLEUR - GET_EQUIPES (GET /equipes)
# ============================================================

def test_controller_get_equipes():
    """Vérifie que le contrôleur renvoie les équipes fournies par le service."""
    resultat = get_equipes()
    assert len(resultat) == len(equipes)
    assert resultat == EquipeService.lister_equipes()


# ============================================================
# TESTS : CONTRÔLEUR - POST_EQUIPE (POST /equipes)
# ============================================================

def test_controller_post_equipe():
    """Vérifie que le contrôleur crée une équipe via le service."""
    avant = len(equipes)
    tournoi_id = equipes[0]["tournoi_id"]
    payload = EquipeCreate(nom="Les Faucons", tournoi_id=tournoi_id, joueurs_ids=[1, 2])

    equipe = post_equipe(payload)

    assert equipe["nom"] == "Les Faucons"
    assert equipe["tournoi_id"] == tournoi_id
    assert equipe["joueurs_ids"] == [1, 2]
    assert equipe in EquipeService.lister_equipes()
    assert len(equipes) == avant + 1


def test_controller_post_equipe_tournoi_inexistant():
    """Vérifie que le contrôleur transforme l'erreur du service en 400."""
    avant = len(equipes)
    with pytest.raises(HTTPException) as erreur:
        post_equipe(EquipeCreate(nom="Fantômes", tournoi_id=999))
    assert erreur.value.status_code == 400
    assert "999" in erreur.value.detail
    assert len(equipes) == avant


# ============================================================
# TESTS : CONTRÔLEUR - GET_EQUIPE_DETAIL (GET /equipes/{equipe_id})
# ============================================================

def test_controller_get_equipe_detail():
    """Vérifie que le contrôleur renvoie le détail enrichi de l'équipe."""
    equipe_id = equipes[0]["id"]
    detail = get_equipe_detail(equipe_id)

    assert detail["id"] == equipe_id
    assert detail["tournoi"] == get_tournoi(equipes[0]["tournoi_id"])
    assert len(detail["joueurs"]) == len(equipes[0]["joueurs_ids"])
    assert detail == EquipeService.obtenir_equipe_detail(equipe_id)


def test_controller_get_equipe_detail_inexistante():
    """Vérifie qu'un ID d'équipe inconnu renvoie une 404."""
    with pytest.raises(HTTPException) as erreur:
        get_equipe_detail(999)
    assert erreur.value.status_code == 404
    assert erreur.value.detail == "Equipe introuvable"


# ============================================================
# BLOC D'EXÉCUTION EN BAS DU FICHIER (Pour lancer le rapport)
# ============================================================
if __name__ == "__main__":
    pytest.main(["-v", __file__])