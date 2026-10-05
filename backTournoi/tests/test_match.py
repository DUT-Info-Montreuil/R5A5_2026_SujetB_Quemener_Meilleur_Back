import copy

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

# Importation des données et fonctions d'accès depuis utils/data/data.py
from backTournoi.main.utils.data.data import (
    matchs,
    get_equipe,
)
from backTournoi.main.controllers.match_controller import (
    get_matchs,
    create_match,
    update_match,
)
from backTournoi.main.services.match_service import MatchService
from backTournoi.main.dto.match_dto import MatchCreate, MatchUpdate


@pytest.fixture(autouse=True)
def reinitialiser_donnees():
    """Sauvegarde la liste des matchs avant chaque test et la restaure après,
    pour que les tests de création / modification n'influencent pas les autres."""
    sauvegarde = copy.deepcopy(matchs)
    yield
    matchs[:] = sauvegarde


# ============================================================
# TESTS : SERVICE - LISTER_MATCHS
# ============================================================

def test_lister_matchs_volumetrie():
    """Vérifie que le service renvoie tous les matchs des données factices."""
    resultat = MatchService.lister_matchs()
    assert len(resultat) == 12
    assert resultat is matchs


def test_lister_matchs_structure():
    """Vérifie que chaque match contient les champs attendus."""
    champs = {"id", "equipe1_id", "equipe2_id", "score_equipe1", "score_equipe2"}
    for match in MatchService.lister_matchs():
        assert champs.issubset(match.keys())


def test_lister_matchs_equipes_existantes():
    """Vérifie que les deux équipes de chaque match existent bien."""
    for match in MatchService.lister_matchs():
        assert get_equipe(match["equipe1_id"]) is not None
        assert get_equipe(match["equipe2_id"]) is not None


# ============================================================
# TESTS : SERVICE - CREER_MATCH
# ============================================================

def test_creer_match():
    """Vérifie la création d'un match avec tous les champs."""
    nouvel_id = max(m["id"] for m in matchs) + 1
    payload = MatchCreate(equipe1_id=1, equipe2_id=2, score_equipe1=2, score_equipe2=5)

    match = MatchService.creer_match(payload)

    assert match["id"] == nouvel_id
    assert match["equipe1_id"] == 1
    assert match["equipe2_id"] == 2
    assert match["score_equipe1"] == 2
    assert match["score_equipe2"] == 5


def test_creer_match_ajoute_a_la_liste():
    """Vérifie que le match créé est bien ajouté à la liste des matchs."""
    MatchService.creer_match(MatchCreate(equipe1_id=1, equipe2_id=2))
    assert len(matchs) == 13


def test_creer_match_scores_par_defaut():
    """Vérifie que les scores valent 0 quand ils ne sont pas fournis."""
    match = MatchService.creer_match(MatchCreate(equipe1_id=1, equipe2_id=2))
    assert match["score_equipe1"] == 0
    assert match["score_equipe2"] == 0


def test_creer_match_ids_uniques():
    """Vérifie que deux créations successives reçoivent des ID différents."""
    m1 = MatchService.creer_match(MatchCreate(equipe1_id=1, equipe2_id=2))
    m2 = MatchService.creer_match(MatchCreate(equipe1_id=3, equipe2_id=4))
    assert m1["id"] != m2["id"]


def test_creer_match_meme_equipe():
    """Vérifie qu'un match d'une équipe contre elle-même est refusé."""
    with pytest.raises(ValueError):
        MatchService.creer_match(MatchCreate(equipe1_id=1, equipe2_id=1))
    assert len(matchs) == 12


def test_creer_match_equipe_inexistante():
    """Vérifie qu'un match avec une équipe inconnue est refusé."""
    with pytest.raises(ValueError, match="999"):
        MatchService.creer_match(MatchCreate(equipe1_id=1, equipe2_id=999))
    assert len(matchs) == 12


def test_creer_match_equipe_manquante():
    """Vérifie qu'un payload sans equipe2_id est rejeté par le DTO."""
    with pytest.raises(ValidationError):
        MatchCreate(equipe1_id=1)


def test_creer_match_score_invalide():
    """Vérifie qu'un score qui n'est pas un entier est rejeté par le DTO."""
    with pytest.raises(ValidationError):
        MatchCreate(equipe1_id=1, equipe2_id=2, score_equipe1="beaucoup")


# ============================================================
# TESTS : SERVICE - MODIFIER_MATCH
# ============================================================

def test_modifier_match_scores():
    """Vérifie la modification des scores d'un match existant."""
    match_id = matchs[0]["id"]
    match = MatchService.modifier_match(match_id, MatchUpdate(score_equipe1=10, score_equipe2=7))

    assert match is not None
    assert match["id"] == match_id
    assert match["score_equipe1"] == 10
    assert match["score_equipe2"] == 7


def test_modifier_match_partielle():
    """Vérifie que les champs non envoyés ne sont pas modifiés."""
    avant = copy.deepcopy(matchs[0])
    match = MatchService.modifier_match(avant["id"], MatchUpdate(score_equipe1=99))

    assert match["score_equipe1"] == 99
    assert match["score_equipe2"] == avant["score_equipe2"]
    assert match["equipe1_id"] == avant["equipe1_id"]
    assert match["equipe2_id"] == avant["equipe2_id"]


def test_modifier_match_equipes():
    """Vérifie la modification des équipes d'un match."""
    match_id = matchs[0]["id"]
    match = MatchService.modifier_match(match_id, MatchUpdate(equipe1_id=3, equipe2_id=4))

    assert match["equipe1_id"] == 3
    assert match["equipe2_id"] == 4


def test_modifier_match_persistant():
    """Vérifie que la modification est bien visible dans la liste des matchs."""
    match_id = matchs[0]["id"]
    MatchService.modifier_match(match_id, MatchUpdate(score_equipe2=8))

    match = next(m for m in MatchService.lister_matchs() if m["id"] == match_id)
    assert match["score_equipe2"] == 8


def test_modifier_match_ne_change_pas_le_nombre_de_matchs():
    """Vérifie qu'une modification ne crée ni ne supprime de match."""
    MatchService.modifier_match(matchs[0]["id"], MatchUpdate(score_equipe1=5))
    assert len(matchs) == 12


def test_modifier_match_inexistant():
    """Vérifie qu'un ID de match inconnu renvoie None."""
    assert MatchService.modifier_match(999, MatchUpdate(score_equipe1=1)) is None


def test_modifier_match_equipe_inexistante():
    """Vérifie qu'une modification vers une équipe inconnue est refusée."""
    avant = copy.deepcopy(matchs[0])
    with pytest.raises(ValueError, match="999"):
        MatchService.modifier_match(avant["id"], MatchUpdate(equipe1_id=999))
    assert matchs[0] == avant


def test_modifier_match_meme_equipe():
    """Vérifie qu'on ne peut pas opposer une équipe à elle-même."""
    avant = copy.deepcopy(matchs[0])
    with pytest.raises(ValueError):
        MatchService.modifier_match(
            avant["id"], MatchUpdate(equipe1_id=avant["equipe2_id"])
        )
    assert matchs[0] == avant


def test_modifier_match_score_invalide():
    """Vérifie qu'un score qui n'est pas un entier est rejeté par le DTO."""
    with pytest.raises(ValidationError):
        MatchUpdate(score_equipe1="beaucoup")


# ============================================================
# TESTS : CONTRÔLEUR - GET_MATCHS (GET /match)
# ============================================================

def test_controller_get_matchs():
    """Vérifie que le contrôleur renvoie les matchs fournis par le service."""
    resultat = get_matchs()
    assert len(resultat) == 12
    assert resultat == MatchService.lister_matchs()


# ============================================================
# TESTS : CONTRÔLEUR - CREATE_MATCH (POST /match)
# ============================================================

def test_controller_create_match():
    """Vérifie que le contrôleur crée un match via le service."""
    payload = MatchCreate(equipe1_id=1, equipe2_id=2, score_equipe1=2, score_equipe2=5)

    match = create_match(payload)

    assert match["equipe1_id"] == 1
    assert match["equipe2_id"] == 2
    assert match["score_equipe1"] == 2
    assert match["score_equipe2"] == 5
    assert match in MatchService.lister_matchs()
    assert len(matchs) == 13


def test_controller_create_match_meme_equipe():
    """Vérifie que le contrôleur transforme l'erreur du service en 400."""
    with pytest.raises(HTTPException) as erreur:
        create_match(MatchCreate(equipe1_id=1, equipe2_id=1))
    assert erreur.value.status_code == 400
    assert len(matchs) == 12


def test_controller_create_match_equipe_inexistante():
    """Vérifie qu'une équipe inconnue est refusée avec un 400."""
    with pytest.raises(HTTPException) as erreur:
        create_match(MatchCreate(equipe1_id=1, equipe2_id=999))
    assert erreur.value.status_code == 400
    assert "999" in erreur.value.detail


# ============================================================
# TESTS : CONTRÔLEUR - UPDATE_MATCH (PUT /match/{match_id})
# ============================================================

def test_controller_update_match():
    """Vérifie que le contrôleur modifie un match via le service."""
    match_id = matchs[0]["id"]
    match = update_match(match_id, MatchUpdate(score_equipe1=10, score_equipe2=7))

    assert match["id"] == match_id
    assert match["score_equipe1"] == 10
    assert match["score_equipe2"] == 7
    assert get_matchs()[0]["score_equipe1"] == 10


def test_controller_update_match_inexistant():
    """Vérifie qu'un ID de match inconnu renvoie une 404."""
    with pytest.raises(HTTPException) as erreur:
        update_match(999, MatchUpdate(score_equipe1=1))
    assert erreur.value.status_code == 404
    assert erreur.value.detail == "Match introuvable"


def test_controller_update_match_equipe_inexistante():
    """Vérifie qu'une modification vers une équipe inconnue renvoie un 400."""
    avant = copy.deepcopy(matchs[0])
    with pytest.raises(HTTPException) as erreur:
        update_match(avant["id"], MatchUpdate(equipe1_id=999))
    assert erreur.value.status_code == 400
    assert matchs[0] == avant


# ============================================================
# BLOC D'EXÉCUTION EN BAS DU FICHIER (Pour lancer le rapport)
# ============================================================
if __name__ == "__main__":
    pytest.main(["-v", __file__])
