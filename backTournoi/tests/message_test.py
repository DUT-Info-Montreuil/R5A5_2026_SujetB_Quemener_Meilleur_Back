import copy

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

# Importation des données et fonctions d'accès depuis utils/data/data.py
from backTournoi.main.utils.data.data import (
    messages,
    equipes,
    tournois,
    get_equipe,
    get_utilisateur,
)
from backTournoi.main.controllers.message_controller import (
    get_messages,
    post_message,
    get_message_detail,
)
from backTournoi.main.services.message_service import MessageService
from backTournoi.main.dto.message_dto import MessageCreate


@pytest.fixture(autouse=True)
def reinitialiser_donnees():
    """Sauvegarde les messages avant chaque test et les restaure après,
    pour que les tests de création n'influencent pas les autres."""
    sauvegarde_messages = copy.deepcopy(messages)
    yield
    messages[:] = sauvegarde_messages


def payload_valide(**kwargs):
    """Construit un MessageCreate valide (auteur membre de la première équipe),
    avec possibilité de surcharger des champs."""
    equipe = equipes[0]
    donnees = dict(
        equipe_id=equipe["id"],
        utilisateur_id=equipe["joueurs_ids"][0],
        message="Salut l'équipe !",
    )
    donnees.update(kwargs)
    return MessageCreate(**donnees)


def utilisateur_hors_equipe(equipe):
    """Renvoie l'ID d'un utilisateur existant qui n'est pas membre de l'équipe,
    ou None si on n'en trouve pas dans les données factices."""
    for autre in equipes:
        for uid in autre["joueurs_ids"]:
            if uid not in equipe["joueurs_ids"] and get_utilisateur(uid) is not None:
                return uid
    return None


# ============================================================
# TESTS : SERVICE - LISTER_MESSAGES
# ============================================================

def test_lister_messages_non_vide():
    """Vérifie que le service renvoie bien la liste des messages des données factices."""
    resultat = MessageService.lister_messages()
    assert len(resultat) > 0
    assert resultat is messages


def test_lister_messages_structure():
    """Vérifie que chaque message contient les champs attendus."""
    champs = {"id", "equipe_id", "utilisateur_id", "message"}
    for message in MessageService.lister_messages():
        assert champs.issubset(message.keys())


def test_lister_messages_ids_uniques():
    """Vérifie qu'il n'y a pas deux messages avec le même ID."""
    ids = [m["id"] for m in MessageService.lister_messages()]
    assert len(ids) == len(set(ids))


def test_lister_messages_equipes_existantes():
    """Vérifie que chaque message appartient à une équipe qui existe."""
    for message in MessageService.lister_messages():
        assert get_equipe(message["equipe_id"]) is not None


def test_lister_messages_auteurs_existants():
    """Vérifie que l'auteur de chaque message existe bien."""
    for message in MessageService.lister_messages():
        assert get_utilisateur(message["utilisateur_id"]) is not None


def test_lister_messages_filtre_par_equipe():
    """Vérifie que le filtre ne renvoie que les messages de l'équipe demandée."""
    equipe_id = messages[0]["equipe_id"]
    resultat = MessageService.lister_messages(equipe_id)

    attendus = [m for m in messages if m["equipe_id"] == equipe_id]
    assert resultat == attendus
    assert len(resultat) > 0
    for message in resultat:
        assert message["equipe_id"] == equipe_id


def test_lister_messages_filtre_equipe_inconnue():
    """Vérifie qu'une équipe inconnue renvoie une liste vide."""
    assert MessageService.lister_messages(999) == []


# ============================================================
# TESTS : SERVICE - OBTENIR_MESSAGE
# ============================================================

def test_obtenir_message():
    """Vérifie qu'un message existant est renvoyé par son ID."""
    attendu = messages[0]
    message = MessageService.obtenir_message(attendu["id"])
    assert message == attendu


def test_obtenir_message_inexistant():
    """Vérifie qu'un ID de message inconnu renvoie None."""
    assert MessageService.obtenir_message(999) is None


# ============================================================
# TESTS : SERVICE - CREER_MESSAGE
# ============================================================

def test_creer_message():
    """Vérifie la création d'un message avec tous les champs."""
    nouvel_id = max(m["id"] for m in messages) + 1
    equipe = equipes[0]

    message = MessageService.creer_message(payload_valide())

    assert message["id"] == nouvel_id
    assert message["equipe_id"] == equipe["id"]
    assert message["utilisateur_id"] == equipe["joueurs_ids"][0]
    assert message["message"] == "Salut l'équipe !"


def test_creer_message_ajoute_a_la_liste():
    """Vérifie que le message créé est bien ajouté à la liste des messages."""
    avant = len(messages)
    message = MessageService.creer_message(payload_valide())
    assert len(messages) == avant + 1
    assert MessageService.obtenir_message(message["id"]) == message


def test_creer_message_visible_dans_son_equipe():
    """Vérifie que le message créé apparaît dans les messages de son équipe."""
    equipe_id = equipes[0]["id"]
    message = MessageService.creer_message(payload_valide())
    assert message in MessageService.lister_messages(equipe_id)


def test_creer_message_ids_uniques():
    """Vérifie que deux créations successives reçoivent des ID différents."""
    m1 = MessageService.creer_message(payload_valide(message="Premier"))
    m2 = MessageService.creer_message(payload_valide(message="Second"))
    assert m1["id"] != m2["id"]


def test_creer_message_equipe_inexistante():
    """Vérifie qu'une équipe inconnue est refusée et sans effet."""
    avant = len(messages)
    with pytest.raises(ValueError, match="équipe"):
        MessageService.creer_message(payload_valide(equipe_id=999))
    assert len(messages) == avant


def test_creer_message_utilisateur_inexistant():
    """Vérifie qu'un auteur inconnu est refusé et sans effet."""
    avant = len(messages)
    with pytest.raises(ValueError, match="utilisateur"):
        MessageService.creer_message(payload_valide(utilisateur_id=999))
    assert len(messages) == avant


def test_creer_message_auteur_non_membre():
    """Vérifie qu'un utilisateur qui n'est pas dans l'équipe ne peut pas y écrire."""
    equipe = equipes[0]
    intrus = utilisateur_hors_equipe(equipe)
    if intrus is None:
        pytest.skip("Aucun utilisateur extérieur à l'équipe dans les données factices")

    avant = len(messages)
    with pytest.raises(ValueError, match="membre"):
        MessageService.creer_message(payload_valide(utilisateur_id=intrus))
    assert len(messages) == avant


def test_creer_message_texte_vide():
    """Vérifie qu'un contenu vide est rejeté par le DTO."""
    with pytest.raises(ValidationError):
        payload_valide(message="")


def test_creer_message_texte_blanc():
    """Vérifie qu'un contenu composé uniquement d'espaces est rejeté par le DTO."""
    with pytest.raises(ValidationError):
        payload_valide(message="   ")


def test_creer_message_texte_trop_long():
    """Vérifie qu'un contenu de plus de 500 caractères est rejeté par le DTO."""
    with pytest.raises(ValidationError):
        payload_valide(message="x" * 501)


def test_creer_message_texte_longueur_max():
    """Vérifie qu'un contenu de exactement 500 caractères est accepté."""
    message = MessageService.creer_message(payload_valide(message="x" * 500))
    assert len(message["message"]) == 500


def test_creer_message_equipe_id_invalide():
    """Vérifie qu'un equipe_id qui n'est pas un entier est rejeté par le DTO."""
    with pytest.raises(ValidationError):
        payload_valide(equipe_id="abc")


def test_creer_message_utilisateur_id_invalide():
    """Vérifie qu'un utilisateur_id qui n'est pas un entier est rejeté par le DTO."""
    with pytest.raises(ValidationError):
        payload_valide(utilisateur_id="abc")


def test_creer_message_champ_manquant():
    """Vérifie que tous les champs du DTO de création sont obligatoires."""
    with pytest.raises(ValidationError):
        MessageCreate(equipe_id=1, utilisateur_id=1)
    with pytest.raises(ValidationError):
        MessageCreate(equipe_id=1, message="Salut")
    with pytest.raises(ValidationError):
        MessageCreate(utilisateur_id=1, message="Salut")


# ============================================================
# TESTS : CONTRÔLEUR - GET_MESSAGES (GET /messages)
# ============================================================

def test_controller_get_messages():
    """Vérifie que le contrôleur renvoie les messages fournis par le service."""
    resultat = get_messages()
    assert len(resultat) == len(messages)
    assert resultat == MessageService.lister_messages()


def test_controller_get_messages_filtre_par_equipe():
    """Vérifie que le contrôleur filtre les messages par équipe."""
    equipe_id = messages[0]["equipe_id"]
    resultat = get_messages(equipe_id=equipe_id)
    assert resultat == MessageService.lister_messages(equipe_id)
    for message in resultat:
        assert message["equipe_id"] == equipe_id


def test_controller_get_messages_equipe_inconnue():
    """Vérifie qu'une équipe inconnue renvoie une liste vide."""
    assert get_messages(equipe_id=999) == []


# ============================================================
# TESTS : CONTRÔLEUR - POST_MESSAGE (POST /messages)
# ============================================================

def test_controller_post_message():
    """Vérifie que le contrôleur crée un message via le service."""
    avant = len(messages)

    message = post_message(payload_valide())

    assert message["message"] == "Salut l'équipe !"
    assert message["equipe_id"] == equipes[0]["id"]
    assert message in MessageService.lister_messages()
    assert len(messages) == avant + 1


def test_controller_post_message_equipe_inexistante():
    """Vérifie que le contrôleur transforme l'erreur du service en 400."""
    with pytest.raises(HTTPException) as erreur:
        post_message(payload_valide(equipe_id=999))
    assert erreur.value.status_code == 400
    assert "n'existe pas" in erreur.value.detail


def test_controller_post_message_utilisateur_inexistant():
    """Vérifie que le contrôleur renvoie une 400 pour un auteur inconnu."""
    with pytest.raises(HTTPException) as erreur:
        post_message(payload_valide(utilisateur_id=999))
    assert erreur.value.status_code == 400
    assert "n'existe pas" in erreur.value.detail


def test_controller_post_message_auteur_non_membre():
    """Vérifie que le contrôleur renvoie une 400 pour un auteur hors de l'équipe."""
    intrus = utilisateur_hors_equipe(equipes[0])
    if intrus is None:
        pytest.skip("Aucun utilisateur extérieur à l'équipe dans les données factices")

    with pytest.raises(HTTPException) as erreur:
        post_message(payload_valide(utilisateur_id=intrus))
    assert erreur.value.status_code == 400
    assert "membre" in erreur.value.detail


# ============================================================
# TESTS : CONTRÔLEUR - GET_MESSAGE_DETAIL (GET /messages/{message_id})
# ============================================================

def test_controller_get_message_detail():
    """Vérifie que le contrôleur renvoie le message demandé."""
    message_id = messages[0]["id"]
    message = get_message_detail(message_id)
    assert message["id"] == message_id
    assert message == MessageService.obtenir_message(message_id)


def test_controller_get_message_detail_inexistant():
    """Vérifie qu'un ID de message inconnu renvoie une 404."""
    with pytest.raises(HTTPException) as erreur:
        get_message_detail(999)
    assert erreur.value.status_code == 404
    assert erreur.value.detail == "Message introuvable"


# ============================================================
# BLOC D'EXÉCUTION EN BAS DU FICHIER (Pour lancer le rapport)
# ============================================================
if __name__ == "__main__":
    pytest.main(["-v", __file__])