import copy

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

# Importation des données et fonctions d'accès depuis utils/data/data.py
from backTournoi.main.utils.data.data import (
    utilisateurs,
    equipes,
    messages,
    get_utilisateur,
)
from backTournoi.main.controllers.utilisateur_controller import (
    get_utilisateurs,
    post_utilisateur,
    get_utilisateur_detail,
    patch_utilisateur,
)
from backTournoi.main.services.utilisateur_service import UtilisateurService
from backTournoi.main.dto.utilisateur_dto import (
    UtilisateurCreate,
    UtilisateurUpdate,
    UtilisateurOut,
)


@pytest.fixture(autouse=True)
def reinitialiser_donnees():
    """Sauvegarde la liste des utilisateurs avant chaque test et la restaure après,
    pour que les tests de création / modification n'influencent pas les autres
    (le PATCH modifie le dictionnaire de l'utilisateur en place)."""
    sauvegarde_utilisateurs = copy.deepcopy(utilisateurs)
    yield
    utilisateurs[:] = sauvegarde_utilisateurs


def payload_valide(**kwargs):
    """Construit un UtilisateurCreate valide, avec possibilité de surcharger des champs."""
    donnees = dict(login="nouveau_joueur", mdp="secret123", is_admin=False)
    donnees.update(kwargs)
    return UtilisateurCreate(**donnees)


# ============================================================
# TESTS : SERVICE - LISTER / OBTENIR
# ============================================================

def test_lister_utilisateurs():
    """Vérifie que le service renvoie la liste des utilisateurs, avec ID et logins uniques."""
    resultat = UtilisateurService.lister_utilisateurs()
    assert len(resultat) > 0
    assert resultat is utilisateurs
    ids = [u["id"] for u in resultat]
    logins = [u["login"] for u in resultat]
    assert len(ids) == len(set(ids))
    assert len(logins) == len(set(logins))


def test_obtenir_utilisateur():
    """Vérifie qu'un utilisateur existant est renvoyé par son ID, sans enrichissement."""
    attendu = utilisateurs[0]
    utilisateur = UtilisateurService.obtenir_utilisateur(attendu["id"])
    assert utilisateur == attendu
    assert "equipes" not in utilisateur
    assert "messages" not in utilisateur


def test_obtenir_utilisateur_inexistant():
    """Vérifie qu'un ID d'utilisateur inconnu renvoie None."""
    assert UtilisateurService.obtenir_utilisateur(999) is None


# ============================================================
# TESTS : SERVICE - OBTENIR_UTILISATEUR_DETAIL
# ============================================================

def test_obtenir_utilisateur_detail():
    """Vérifie que le détail contient ses équipes et ses messages, et seulement eux."""
    utilisateur_id = utilisateurs[0]["id"]
    detail = UtilisateurService.obtenir_utilisateur_detail(utilisateur_id)

    assert detail["id"] == utilisateur_id
    assert detail["equipes"] == [e for e in equipes if utilisateur_id in e["joueurs_ids"]]
    assert detail["messages"] == [m for m in messages if m["utilisateur_id"] == utilisateur_id]
    # L'enrichissement ne doit pas modifier l'utilisateur stocké
    assert "equipes" not in get_utilisateur(utilisateur_id)


def test_obtenir_utilisateur_detail_sans_equipe_ni_message():
    """Vérifie qu'un utilisateur fraîchement créé renvoie des listes vides."""
    utilisateur = UtilisateurService.creer_utilisateur(payload_valide())
    detail = UtilisateurService.obtenir_utilisateur_detail(utilisateur["id"])
    assert detail["equipes"] == []
    assert detail["messages"] == []


def test_obtenir_utilisateur_detail_inexistant():
    """Vérifie qu'un ID d'utilisateur inconnu renvoie None."""
    assert UtilisateurService.obtenir_utilisateur_detail(999) is None


# ============================================================
# TESTS : SERVICE - CREER_UTILISATEUR
# ============================================================

def test_creer_utilisateur():
    """Vérifie la création : champs, ID, ajout à la liste et non-admin par défaut."""
    nouvel_id = max(u["id"] for u in utilisateurs) + 1
    avant = len(utilisateurs)

    utilisateur = UtilisateurService.creer_utilisateur(
        UtilisateurCreate(login="nouveau_joueur", mdp="secret123")
    )

    assert utilisateur["id"] == nouvel_id
    assert utilisateur["login"] == "nouveau_joueur"
    assert utilisateur["mdp"] == "secret123"
    assert utilisateur["is_admin"] is False
    assert len(utilisateurs) == avant + 1
    assert get_utilisateur(nouvel_id) == utilisateur


def test_creer_utilisateur_login_deja_pris():
    """Vérifie qu'un login déjà utilisé est refusé et sans effet."""
    avant = len(utilisateurs)
    with pytest.raises(ValueError, match="existe déjà"):
        UtilisateurService.creer_utilisateur(
            payload_valide(login=utilisateurs[0]["login"])
        )
    assert len(utilisateurs) == avant


@pytest.mark.parametrize("champ, valeur", [
    ("login", ""),
    ("login", "x" * 51),
    ("mdp", ""),
    ("mdp", "x" * 51),
])
def test_creer_utilisateur_donnees_invalides(champ, valeur):
    """Vérifie que le DTO rejette un login ou un mot de passe vide ou trop long (> 50)."""
    with pytest.raises(ValidationError):
        payload_valide(**{champ: valeur})


def test_utilisateur_out_sans_mdp():
    """Vérifie que le mot de passe n'est jamais exposé par le DTO de sortie."""
    utilisateur = UtilisateurService.creer_utilisateur(payload_valide())
    sortie = UtilisateurOut.model_validate(utilisateur).model_dump()
    assert "mdp" not in sortie
    assert sortie["login"] == "nouveau_joueur"


# ============================================================
# TESTS : SERVICE - MODIFIER_UTILISATEUR
# ============================================================

def test_modifier_utilisateur():
    """Vérifie la modification de plusieurs champs, bien enregistrée dans les données."""
    utilisateur_id = utilisateurs[0]["id"]
    payload = UtilisateurUpdate(login="Renommé", mdp="nouveau_mdp", is_admin=True)

    utilisateur = UtilisateurService.modifier_utilisateur(utilisateur_id, payload)

    assert utilisateur["login"] == "Renommé"
    assert utilisateur["mdp"] == "nouveau_mdp"
    assert utilisateur["is_admin"] is True
    assert get_utilisateur(utilisateur_id) == utilisateur


def test_modifier_utilisateur_ne_touche_pas_les_autres_champs():
    """Vérifie que les champs non fournis restent inchangés."""
    avant = copy.deepcopy(utilisateurs[0])
    UtilisateurService.modifier_utilisateur(
        avant["id"], UtilisateurUpdate(login="Renommé")
    )

    apres = get_utilisateur(avant["id"])
    for champ in avant:
        if champ != "login":
            assert apres[champ] == avant[champ]


def test_modifier_utilisateur_inexistant():
    """Vérifie qu'un ID d'utilisateur inconnu renvoie None."""
    assert UtilisateurService.modifier_utilisateur(
        999, UtilisateurUpdate(login="Fantôme")
    ) is None


def test_modifier_utilisateur_login_deja_pris():
    """Vérifie qu'on ne peut pas prendre le login d'un autre, et que rien n'est modifié."""
    avant = copy.deepcopy(utilisateurs[0])
    with pytest.raises(ValueError, match="existe déjà"):
        UtilisateurService.modifier_utilisateur(
            avant["id"],
            UtilisateurUpdate(mdp="autre_mdp", login=utilisateurs[1]["login"]),
        )
    assert get_utilisateur(avant["id"]) == avant


def test_modifier_utilisateur_meme_login_tolere():
    """Vérifie que renvoyer son propre login n'est pas une erreur."""
    login = utilisateurs[0]["login"]
    utilisateur = UtilisateurService.modifier_utilisateur(
        utilisateurs[0]["id"], UtilisateurUpdate(login=login)
    )
    assert utilisateur["login"] == login


@pytest.mark.parametrize("champ", ["login", "mdp", "is_admin"])
def test_modifier_utilisateur_champ_null(champ):
    """Vérifie qu'on ne peut mettre à null ni le login, ni le mdp, ni is_admin."""
    with pytest.raises(ValueError, match=champ):
        UtilisateurService.modifier_utilisateur(
            utilisateurs[0]["id"], UtilisateurUpdate(**{champ: None})
        )


# ============================================================
# TESTS : CONTRÔLEUR
# ============================================================

def test_controller_get_utilisateurs():
    """Vérifie que le contrôleur renvoie les utilisateurs fournis par le service."""
    assert get_utilisateurs() == UtilisateurService.lister_utilisateurs()


def test_controller_post_utilisateur():
    """Vérifie que le contrôleur crée un utilisateur via le service."""
    avant = len(utilisateurs)
    utilisateur = post_utilisateur(payload_valide())
    assert utilisateur["login"] == "nouveau_joueur"
    assert len(utilisateurs) == avant + 1


def test_controller_post_utilisateur_login_deja_pris():
    """Vérifie que le contrôleur transforme l'erreur du service en 400."""
    with pytest.raises(HTTPException) as erreur:
        post_utilisateur(payload_valide(login=utilisateurs[0]["login"]))
    assert erreur.value.status_code == 400
    assert "existe déjà" in erreur.value.detail


def test_controller_get_utilisateur_detail():
    """Vérifie que le contrôleur renvoie le détail enrichi de l'utilisateur."""
    utilisateur_id = utilisateurs[0]["id"]
    detail = get_utilisateur_detail(utilisateur_id)
    assert detail == UtilisateurService.obtenir_utilisateur_detail(utilisateur_id)


def test_controller_get_utilisateur_detail_inexistant():
    """Vérifie qu'un ID d'utilisateur inconnu renvoie une 404."""
    with pytest.raises(HTTPException) as erreur:
        get_utilisateur_detail(999)
    assert erreur.value.status_code == 404
    assert erreur.value.detail == "Utilisateur introuvable"


def test_controller_patch_utilisateur():
    """Vérifie que le contrôleur modifie un utilisateur via le service."""
    utilisateur_id = utilisateurs[0]["id"]
    utilisateur = patch_utilisateur(utilisateur_id, UtilisateurUpdate(login="Renommé"))
    assert utilisateur["login"] == "Renommé"
    assert get_utilisateur(utilisateur_id)["login"] == "Renommé"


def test_controller_patch_utilisateur_inexistant():
    """Vérifie qu'un ID d'utilisateur inconnu renvoie une 404."""
    with pytest.raises(HTTPException) as erreur:
        patch_utilisateur(999, UtilisateurUpdate(login="Fantôme"))
    assert erreur.value.status_code == 404
    assert erreur.value.detail == "Utilisateur introuvable"


def test_controller_patch_utilisateur_login_deja_pris():
    """Vérifie que le contrôleur transforme le login en doublon en 400."""
    with pytest.raises(HTTPException) as erreur:
        patch_utilisateur(
            utilisateurs[0]["id"], UtilisateurUpdate(login=utilisateurs[1]["login"])
        )
    assert erreur.value.status_code == 400
    assert "existe déjà" in erreur.value.detail


# ============================================================
# BLOC D'EXÉCUTION EN BAS DU FICHIER (Pour lancer le rapport)
# ============================================================
if __name__ == "__main__":
    pytest.main(["-v", __file__])