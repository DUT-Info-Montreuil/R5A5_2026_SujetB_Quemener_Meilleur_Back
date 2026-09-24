import copy

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

# Importation des données et fonctions d'accès depuis utils/data/data.py
from backTournoi.main.utils.data.data import (
    tournois,
    equipes,
    matchs,
    get_tournoi,
    get_equipe,
)
from backTournoi.main.controllers.tournoi_controller import (
    get_tournois,
    post_tournoi,
    get_tournoi_detail,
    patch_tournoi,
)
from backTournoi.main.services.tournoi_service import TournoiService, TRANSITIONS
from backTournoi.main.dto.tournoi_dto import TournoiCreate, TournoiUpdate


@pytest.fixture(autouse=True)
def reinitialiser_donnees():
    """Sauvegarde la liste des tournois avant chaque test et la restaure après,
    pour que les tests de création / modification n'influencent pas les autres
    (le PATCH modifie le dictionnaire du tournoi en place)."""
    sauvegarde_tournois = copy.deepcopy(tournois)
    yield
    tournois[:] = sauvegarde_tournois


def payload_valide(**kwargs):
    """Construit un TournoiCreate valide, avec possibilité de surcharger des champs."""
    donnees = dict(nom="Coupe des Champions", description="Tournoi de test", jeu_id=1)
    donnees.update(kwargs)
    return TournoiCreate(**donnees)


# ============================================================
# TESTS : SERVICE - LISTER_TOURNOIS
# ============================================================

def test_lister_tournois_non_vide():
    """Vérifie que le service renvoie bien la liste des tournois des données factices."""
    resultat = TournoiService.lister_tournois()
    assert len(resultat) > 0
    assert resultat is tournois


def test_lister_tournois_structure():
    """Vérifie que chaque tournoi contient les champs attendus."""
    champs = {"id", "nom", "statut", "equipes_ids"}
    for tournoi in TournoiService.lister_tournois():
        assert champs.issubset(tournoi.keys())


def test_lister_tournois_ids_uniques():
    """Vérifie qu'il n'y a pas deux tournois avec le même ID."""
    ids = [t["id"] for t in TournoiService.lister_tournois()]
    assert len(ids) == len(set(ids))


def test_lister_tournois_statuts_valides():
    """Vérifie que le statut de chaque tournoi fait partie des statuts connus."""
    for tournoi in TournoiService.lister_tournois():
        assert tournoi["statut"] in TRANSITIONS


def test_lister_tournois_equipes_existantes():
    """Vérifie que toutes les équipes de chaque tournoi existent bien."""
    for tournoi in TournoiService.lister_tournois():
        for equipe_id in tournoi["equipes_ids"]:
            assert get_equipe(equipe_id) is not None


# ============================================================
# TESTS : SERVICE - OBTENIR_TOURNOI
# ============================================================

def test_obtenir_tournoi():
    """Vérifie qu'un tournoi existant est renvoyé par son ID."""
    attendu = tournois[0]
    tournoi = TournoiService.obtenir_tournoi(attendu["id"])
    assert tournoi == attendu


def test_obtenir_tournoi_sans_enrichissement():
    """Vérifie que le tournoi simple ne contient pas les champs enrichis."""
    tournoi = TournoiService.obtenir_tournoi(tournois[0]["id"])
    for champ in ("equipes", "matchs"):
        assert champ not in tournoi


def test_obtenir_tournoi_inexistant():
    """Vérifie qu'un ID de tournoi inconnu renvoie None."""
    assert TournoiService.obtenir_tournoi(999) is None


# ============================================================
# TESTS : SERVICE - OBTENIR_TOURNOI_DETAIL
# ============================================================

def test_obtenir_tournoi_detail_champs():
    """Vérifie que le détail contient les champs de base et les champs enrichis."""
    detail = TournoiService.obtenir_tournoi_detail(tournois[0]["id"])
    champs = {"id", "nom", "statut", "equipes_ids",
              "equipes", "matchs"}
    assert champs.issubset(detail.keys())


def test_obtenir_tournoi_detail_equipes():
    """Vérifie que les équipes sont jointes dans l'ordre de equipes_ids."""
    tournoi = tournois[0]
    detail = TournoiService.obtenir_tournoi_detail(tournoi["id"])
    assert len(detail["equipes"]) == len(tournoi["equipes_ids"])
    assert [e["id"] for e in detail["equipes"]] == tournoi["equipes_ids"]


def test_obtenir_tournoi_detail_matchs():
    """Vérifie que seuls les matchs joués par les équipes du tournoi sont renvoyés."""
    tournoi = tournois[0]
    detail = TournoiService.obtenir_tournoi_detail(tournoi["id"])

    attendus = [m for m in matchs
                if m["equipe1_id"] in tournoi["equipes_ids"]
                or m["equipe2_id"] in tournoi["equipes_ids"]]
    assert detail["matchs"] == attendus
    for match in detail["matchs"]:
        assert (match["equipe1_id"] in tournoi["equipes_ids"]
                or match["equipe2_id"] in tournoi["equipes_ids"])


def test_obtenir_tournoi_detail_sans_equipe():
    """Vérifie qu'un tournoi sans équipe renvoie des listes vides."""
    tournoi = TournoiService.creer_tournoi(payload_valide())
    detail = TournoiService.obtenir_tournoi_detail(tournoi["id"])
    assert detail["equipes"] == []
    assert detail["matchs"] == []


def test_obtenir_tournoi_detail_ne_modifie_pas_les_donnees():
    """Vérifie que l'enrichissement n'ajoute rien au tournoi stocké."""
    tournoi_id = tournois[0]["id"]
    TournoiService.obtenir_tournoi_detail(tournoi_id)
    assert "equipes" not in get_tournoi(tournoi_id)
    assert "matchs" not in get_tournoi(tournoi_id)


def test_obtenir_tournoi_detail_inexistant():
    """Vérifie qu'un ID de tournoi inconnu renvoie None."""
    assert TournoiService.obtenir_tournoi_detail(999) is None


# ============================================================
# TESTS : SERVICE - CREER_TOURNOI
# ============================================================

def test_creer_tournoi():
    """Vérifie la création d'un tournoi avec tous les champs."""
    nouvel_id = max(t["id"] for t in tournois) + 1

    tournoi = TournoiService.creer_tournoi(payload_valide())

    assert tournoi["id"] == nouvel_id
    assert tournoi["nom"] == "Coupe des Champions"
    assert tournoi["description"] == "Tournoi de test"
    assert tournoi["jeu_id"] == 1


def test_creer_tournoi_ajoute_a_la_liste():
    """Vérifie que le tournoi créé est bien ajouté à la liste des tournois."""
    avant = len(tournois)
    tournoi = TournoiService.creer_tournoi(payload_valide())
    assert len(tournois) == avant + 1
    assert get_tournoi(tournoi["id"]) == tournoi


def test_creer_tournoi_statut_ouvert():
    """Vérifie que le statut d'un nouveau tournoi est toujours OUVERT."""
    tournoi = TournoiService.creer_tournoi(payload_valide())
    assert tournoi["statut"] == "OUVERT"


def test_creer_tournoi_sans_equipe():
    """Vérifie que la liste d'équipes d'un nouveau tournoi est vide."""
    tournoi = TournoiService.creer_tournoi(payload_valide())
    assert tournoi["equipes_ids"] == []


def test_creer_tournoi_champs_optionnels_par_defaut():
    """Vérifie que description et jeu_id valent None quand ils ne sont pas fournis."""
    tournoi = TournoiService.creer_tournoi(
        TournoiCreate(nom="Minimal")
    )
    assert tournoi["description"] is None
    assert tournoi["jeu_id"] is None


def test_creer_tournoi_ids_uniques():
    """Vérifie que deux créations successives reçoivent des ID différents."""
    t1 = TournoiService.creer_tournoi(payload_valide(nom="Tournoi A"))
    t2 = TournoiService.creer_tournoi(payload_valide(nom="Tournoi B"))
    assert t1["id"] != t2["id"]


def test_creer_tournoi_nom_vide():
    """Vérifie qu'un nom vide est rejeté par le DTO."""
    with pytest.raises(ValidationError):
        payload_valide(nom="")


def test_creer_tournoi_nom_trop_long():
    """Vérifie qu'un nom de plus de 50 caractères est rejeté par le DTO."""
    with pytest.raises(ValidationError):
        payload_valide(nom="x" * 51)


def test_creer_tournoi_jeu_invalide():
    """Vérifie qu'un jeu_id qui n'est pas un entier est rejeté par le DTO."""
    with pytest.raises(ValidationError):
        payload_valide(jeu_id="mario")


def test_creer_tournoi_sans_dates():
    """Vérifie qu'un tournoi peut être créé sans dates."""
    tournoi = TournoiService.creer_tournoi(TournoiCreate(nom="Sans dates"))
    assert "date_debut" not in tournoi
    assert "date_fin" not in tournoi


def test_creer_tournoi_champs_date_absents():
    """Vérifie que le DTO de création ne contient plus de champs de date."""
    payload = TournoiCreate(nom="Sans dates")
    assert "date_debut" not in payload.model_fields
    assert "date_fin" not in payload.model_fields


# ============================================================
# TESTS : SERVICE - MODIFIER_TOURNOI
# ============================================================

def test_modifier_tournoi_nom():
    """Vérifie la modification du nom d'un tournoi."""
    tournoi_id = tournois[0]["id"]
    tournoi = TournoiService.modifier_tournoi(tournoi_id, TournoiUpdate(nom="Renommé"))
    assert tournoi["nom"] == "Renommé"


def test_modifier_tournoi_plusieurs_champs():
    """Vérifie la modification de plusieurs champs en une seule fois."""
    tournoi_id = tournois[0]["id"]
    payload = TournoiUpdate(nom="Renommé", description="Nouvelle description", jeu_id=2)

    tournoi = TournoiService.modifier_tournoi(tournoi_id, payload)

    assert tournoi["nom"] == "Renommé"
    assert tournoi["description"] == "Nouvelle description"
    assert tournoi["jeu_id"] == 2


def test_modifier_tournoi_persiste():
    """Vérifie que la modification est bien enregistrée dans les données."""
    tournoi_id = tournois[0]["id"]
    TournoiService.modifier_tournoi(tournoi_id, TournoiUpdate(nom="Renommé"))
    assert get_tournoi(tournoi_id)["nom"] == "Renommé"


def test_modifier_tournoi_ne_touche_pas_les_autres_champs():
    """Vérifie que les champs non fournis restent inchangés."""
    avant = copy.deepcopy(tournois[0])
    TournoiService.modifier_tournoi(avant["id"], TournoiUpdate(nom="Renommé"))

    apres = get_tournoi(avant["id"])
    for champ in ("description", "statut", "jeu_id", "equipes_ids"):
        assert apres[champ] == avant[champ]


def test_modifier_tournoi_sans_champ():
    """Vérifie qu'un PATCH vide ne change rien."""
    avant = copy.deepcopy(tournois[0])
    tournoi = TournoiService.modifier_tournoi(avant["id"], TournoiUpdate())
    assert tournoi == avant


def test_modifier_tournoi_inexistant():
    """Vérifie qu'un ID de tournoi inconnu renvoie None."""
    assert TournoiService.modifier_tournoi(999, TournoiUpdate(nom="Fantôme")) is None


def test_modifier_tournoi_nom_null():
    """Vérifie qu'on ne peut pas mettre le nom à null."""
    with pytest.raises(ValueError, match="nom"):
        TournoiService.modifier_tournoi(tournois[0]["id"], TournoiUpdate(nom=None))


def test_modifier_tournoi_nom_vide():
    """Vérifie qu'un nom vide est rejeté par le DTO."""
    with pytest.raises(ValidationError):
        TournoiUpdate(nom="")


def test_modifier_tournoi_description():
    """Vérifie que la description peut être modifiée."""
    tournoi_id = tournois[0]["id"]
    tournoi = TournoiService.modifier_tournoi(
        tournoi_id,
        TournoiUpdate(description="Nouvelle description"),
    )
    assert tournoi["description"] == "Nouvelle description"


def test_modifier_tournoi_jeu_id():
    """Vérifie que le jeu associé peut être modifié."""
    tournoi_id = tournois[0]["id"]
    tournoi = TournoiService.modifier_tournoi(
        tournoi_id,
        TournoiUpdate(jeu_id=2),
    )
    assert tournoi["jeu_id"] == 2


# ---------- Statut ----------

@pytest.mark.parametrize("depart, cible", [
    ("OUVERT", "FERME"),
    ("OUVERT", "TERMINE"),
    ("FERME", "EN_COURS"),
    ("FERME", "TERMINE"),
    ("EN_COURS", "TERMINE"),
])
def test_modifier_tournoi_transition_autorisee(depart, cible):
    """Vérifie que les transitions de statut autorisées sont acceptées."""
    tournoi_id = tournois[0]["id"]
    tournois[0]["statut"] = depart

    tournoi = TournoiService.modifier_tournoi(tournoi_id, TournoiUpdate(statut=cible))

    assert tournoi["statut"] == cible
    assert get_tournoi(tournoi_id)["statut"] == cible


@pytest.mark.parametrize("depart, cible", [
    ("OUVERT", "EN_COURS"),
    ("FERME", "OUVERT"),
    ("EN_COURS", "OUVERT"),
    ("TERMINE", "EN_COURS"),
])
def test_modifier_tournoi_transition_interdite(depart, cible):
    """Vérifie que les transitions de statut interdites sont refusées et sans effet."""
    tournoi_id = tournois[0]["id"]
    tournois[0]["statut"] = depart

    with pytest.raises(ValueError, match="Transition"):
        TournoiService.modifier_tournoi(tournoi_id, TournoiUpdate(statut=cible))
    assert get_tournoi(tournoi_id)["statut"] == depart


def test_modifier_tournoi_meme_statut_tolere():
    """Vérifie que renvoyer le statut actuel n'est pas une erreur."""
    tournoi_id = tournois[0]["id"]
    tournois[0]["statut"] = "OUVERT"
    tournoi = TournoiService.modifier_tournoi(tournoi_id, TournoiUpdate(statut="OUVERT"))
    assert tournoi["statut"] == "OUVERT"


def test_modifier_tournoi_statut_inconnu():
    """Vérifie qu'un statut qui n'existe pas est rejeté par le DTO."""
    with pytest.raises(ValidationError):
        TournoiUpdate(statut="BLABLA")


def test_modifier_tournoi_statut_null():
    """Vérifie qu'on ne peut pas mettre le statut à null."""
    with pytest.raises(ValueError, match="statut"):
        TournoiService.modifier_tournoi(tournois[0]["id"], TournoiUpdate(statut=None))


# ============================================================
# TESTS : CONTRÔLEUR - GET_TOURNOIS (GET /tournois)
# ============================================================

def test_controller_get_tournois():
    """Vérifie que le contrôleur renvoie les tournois fournis par le service."""
    resultat = get_tournois()
    assert len(resultat) == len(tournois)
    assert resultat == TournoiService.lister_tournois()


# ============================================================
# TESTS : CONTRÔLEUR - POST_TOURNOI (POST /tournois)
# ============================================================

def test_controller_post_tournoi():
    """Vérifie que le contrôleur crée un tournoi via le service."""
    avant = len(tournois)

    tournoi = post_tournoi(payload_valide())

    assert tournoi["nom"] == "Coupe des Champions"
    assert tournoi["statut"] == "OUVERT"
    assert tournoi["equipes_ids"] == []
    assert tournoi in TournoiService.lister_tournois()
    assert len(tournois) == avant + 1


# ============================================================
# TESTS : CONTRÔLEUR - GET_TOURNOI_DETAIL (GET /tournois/{tournoi_id})
# ============================================================

def test_controller_get_tournoi_detail():
    """Vérifie que le contrôleur renvoie le détail enrichi du tournoi."""
    tournoi_id = tournois[0]["id"]
    detail = get_tournoi_detail(tournoi_id)

    assert detail["id"] == tournoi_id
    assert len(detail["equipes"]) == len(tournois[0]["equipes_ids"])
    assert detail == TournoiService.obtenir_tournoi_detail(tournoi_id)


def test_controller_get_tournoi_detail_inexistant():
    """Vérifie qu'un ID de tournoi inconnu renvoie une 404."""
    with pytest.raises(HTTPException) as erreur:
        get_tournoi_detail(999)
    assert erreur.value.status_code == 404
    assert erreur.value.detail == "Tournoi introuvable"


# ============================================================
# TESTS : CONTRÔLEUR - PATCH_TOURNOI (PATCH /tournois/{tournoi_id})
# ============================================================

def test_controller_patch_tournoi():
    """Vérifie que le contrôleur modifie un tournoi via le service."""
    tournoi_id = tournois[0]["id"]
    tournoi = patch_tournoi(tournoi_id, TournoiUpdate(nom="Renommé"))
    assert tournoi["nom"] == "Renommé"
    assert get_tournoi(tournoi_id)["nom"] == "Renommé"


def test_controller_patch_tournoi_statut():
    """Vérifie que le contrôleur permet de changer le statut d'un tournoi."""
    tournoi_id = tournois[0]["id"]
    tournois[0]["statut"] = "OUVERT"
    tournoi = patch_tournoi(tournoi_id, TournoiUpdate(statut="FERME"))
    assert tournoi["statut"] == "FERME"


def test_controller_patch_tournoi_inexistant():
    """Vérifie qu'un ID de tournoi inconnu renvoie une 404."""
    with pytest.raises(HTTPException) as erreur:
        patch_tournoi(999, TournoiUpdate(nom="Fantôme"))
    assert erreur.value.status_code == 404
    assert erreur.value.detail == "Tournoi introuvable"


def test_controller_patch_tournoi_transition_interdite():
    """Vérifie que le contrôleur transforme l'erreur de transition du service en 400."""
    tournoi_id = tournois[0]["id"]
    tournois[0]["statut"] = "OUVERT"
    with pytest.raises(HTTPException) as erreur:
        patch_tournoi(tournoi_id, TournoiUpdate(statut="EN_COURS"))
    assert erreur.value.status_code == 400
    assert "Transition" in erreur.value.detail
    assert get_tournoi(tournoi_id)["statut"] == "OUVERT"


# ============================================================
# BLOC D'EXÉCUTION EN BAS DU FICHIER (Pour lancer le rapport)
# ============================================================
if __name__ == "__main__":
    pytest.main(["-v", __file__])
