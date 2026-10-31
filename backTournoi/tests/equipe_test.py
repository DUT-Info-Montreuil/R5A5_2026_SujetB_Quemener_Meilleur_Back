import pytest
from fastapi import HTTPException
from pydantic import ValidationError

# Lecture directe de la base de test via les repositories (indépendante des services testés)
from backTournoi.main.utils.data.transaction import transaction
from backTournoi.main.repo.tournoi_repository import TournoiRepository
from backTournoi.main.repo.equipe_repository import EquipeRepository
from backTournoi.main.repo.match_repository import MatchRepository
from backTournoi.main.repo.message_repository import MessageRepository
from backTournoi.main.repo.utilisateur_repository import UtilisateurRepository
from backTournoi.main.controllers.equipe_controller import (
    get_equipes,
    post_equipe,
    get_equipe_detail,
)
from backTournoi.main.services.equipe_service import EquipeService
from backTournoi.main.dto.equipe_dto import EquipeCreate


# L'isolation des tests est assurée par la fixture autouse `base_de_test` (conftest.py) :
# chaque test travaille sur une base SQLite temporaire neuve.

def tournois():
    with transaction() as conn:
        return TournoiRepository.lister(conn)


def equipes():
    with transaction() as conn:
        return EquipeRepository.lister(conn)


def matchs():
    with transaction() as conn:
        return MatchRepository.lister(conn)


def messages():
    with transaction() as conn:
        return MessageRepository.lister(conn)


def get_tournoi(tournoi_id):
    with transaction() as conn:
        return TournoiRepository.obtenir(conn, tournoi_id)


def get_equipe(equipe_id):
    with transaction() as conn:
        return EquipeRepository.obtenir(conn, equipe_id)


def get_utilisateur(utilisateur_id):
    with transaction() as conn:
        return UtilisateurRepository.obtenir(conn, utilisateur_id)


# Utilisateurs de la base de test qui ne font partie d'aucune équipe. Le schéma impose
# « une seule équipe par tournoi et par utilisateur » : on ne peut donc pas réutiliser
# les joueurs d'une équipe existante pour en créer une nouvelle dans le même tournoi.
JOUEURS_LIBRES = [17, 18, 19, 20]
ADMIN_ID = 67


def payload_valide(**kwargs):
    """Construit un EquipeCreate valide, avec possibilité de surcharger des champs."""
    donnees = dict(
        nom="Les Invincibles",
        tournoi_id=tournois()[0]["id"],
        joueurs_ids=[JOUEURS_LIBRES[0], JOUEURS_LIBRES[1]],
    )
    donnees.update(kwargs)
    return EquipeCreate(**donnees)


# ============================================================
# TESTS : SERVICE - LISTER_EQUIPES
# ============================================================

def test_lister_equipes_non_vide():
    """Vérifie que le service renvoie bien la liste des équipes des données factices."""
    resultat = EquipeService.lister_equipes()
    assert len(resultat) > 0
    assert resultat == equipes()


def test_lister_equipes_structure():
    """Vérifie que chaque équipe contient les champs attendus."""
    champs = {"id", "nom", "tournoi_id", "joueurs_ids"}
    for equipe in EquipeService.lister_equipes():
        assert champs.issubset(equipe.keys())


def test_lister_equipes_ids_uniques():
    """Vérifie qu'il n'y a pas deux équipes avec le même ID."""
    ids = [e["id"] for e in EquipeService.lister_equipes()]
    assert len(ids) == len(set(ids))


def test_lister_equipes_tournois_existants():
    """Vérifie que chaque équipe est rattachée à un tournoi qui existe."""
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
    attendu = equipes()[0]
    equipe = EquipeService.obtenir_equipe(attendu["id"])
    assert equipe == attendu


def test_obtenir_equipe_sans_enrichissement():
    """Vérifie que l'équipe simple ne contient pas les champs enrichis."""
    equipe = EquipeService.obtenir_equipe(equipes()[0]["id"])
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
    detail = EquipeService.obtenir_equipe_detail(equipes()[0]["id"])
    champs = {"id", "nom", "tournoi_id", "joueurs_ids",
              "tournoi", "joueurs", "matchs", "messages"}
    assert champs.issubset(detail.keys())


def test_obtenir_equipe_detail_tournoi():
    """Vérifie que le tournoi de l'équipe est bien joint."""
    equipe = equipes()[0]
    detail = EquipeService.obtenir_equipe_detail(equipe["id"])
    assert detail["tournoi"] == get_tournoi(equipe["tournoi_id"])


def test_obtenir_equipe_detail_joueurs():
    """Vérifie que les joueurs sont joints dans l'ordre de joueurs_ids."""
    equipe = equipes()[0]
    detail = EquipeService.obtenir_equipe_detail(equipe["id"])
    assert len(detail["joueurs"]) == len(equipe["joueurs_ids"])
    assert [j["id"] for j in detail["joueurs"]] == equipe["joueurs_ids"]


def test_obtenir_equipe_detail_matchs():
    """Vérifie que seuls les matchs joués par l'équipe sont renvoyés."""
    equipe = equipes()[0]
    detail = EquipeService.obtenir_equipe_detail(equipe["id"])

    attendus = [m for m in matchs()
                if m["equipe1_id"] == equipe["id"]
                or m["equipe2_id"] == equipe["id"]]
    assert detail["matchs"] == attendus
    for match in detail["matchs"]:
        assert equipe["id"] in (match["equipe1_id"], match["equipe2_id"])


def test_obtenir_equipe_detail_messages():
    """Vérifie que seuls les messages de l'équipe sont renvoyés."""
    equipe = equipes()[0]
    detail = EquipeService.obtenir_equipe_detail(equipe["id"])

    attendus = [m for m in messages() if m["equipe_id"] == equipe["id"]]
    assert detail["messages"] == attendus
    for message in detail["messages"]:
        assert message["equipe_id"] == equipe["id"]


def test_obtenir_equipe_detail_sans_match_ni_message():
    """Vérifie qu'une équipe fraîchement créée n'a ni match ni message (et seulement
    ses joueurs : une équipe sans joueur est désormais refusée, voir plus bas)."""
    equipe = EquipeService.creer_equipe(payload_valide())
    detail = EquipeService.obtenir_equipe_detail(equipe["id"])
    assert [j["id"] for j in detail["joueurs"]] == equipe["joueurs_ids"]
    assert detail["matchs"] == []
    assert detail["messages"] == []


def test_obtenir_equipe_detail_ne_modifie_pas_les_donnees():
    """Vérifie que l'enrichissement n'ajoute rien à l'équipe stockée."""
    equipe_id = equipes()[0]["id"]
    EquipeService.obtenir_equipe_detail(equipe_id)
    for champ in ("tournoi", "joueurs", "matchs", "messages"):
        assert champ not in get_equipe(equipe_id)


def test_obtenir_equipe_detail_inexistante():
    """Vérifie qu'un ID d'équipe inconnu renvoie None."""
    assert EquipeService.obtenir_equipe_detail(999) is None


# ============================================================
# TESTS : SERVICE - CREER_EQUIPE
# ============================================================

def test_creer_equipe():
    """Vérifie la création d'une équipe avec tous les champs."""
    nouvel_id = max(e["id"] for e in equipes()) + 1
    joueurs = [JOUEURS_LIBRES[0], JOUEURS_LIBRES[1]]

    equipe = EquipeService.creer_equipe(payload_valide())

    assert equipe["id"] == nouvel_id
    assert equipe["nom"] == "Les Invincibles"
    assert equipe["tournoi_id"] == tournois()[0]["id"]
    assert equipe["joueurs_ids"] == joueurs


def test_creer_equipe_ajoute_a_la_liste():
    """Vérifie que l'équipe créée est bien ajoutée à la liste des équipes."""
    avant = len(equipes())
    equipe = EquipeService.creer_equipe(payload_valide())
    assert len(equipes()) == avant + 1
    assert get_equipe(equipe["id"]) == equipe


def test_creer_equipe_ajoutee_au_tournoi():
    """Vérifie que l'équipe créée est ajoutée aux équipes de son tournoi."""
    tournoi_id = tournois()[0]["id"]
    avant = len(get_tournoi(tournoi_id)["equipes_ids"])

    equipe = EquipeService.creer_equipe(payload_valide(tournoi_id=tournoi_id))

    equipes_ids = get_tournoi(tournoi_id)["equipes_ids"]
    assert len(equipes_ids) == avant + 1
    assert equipe["id"] in equipes_ids


def test_creer_equipe_ne_touche_pas_les_autres_tournois():
    """Vérifie que seuls les équipes_ids du tournoi concerné sont modifiés."""
    tournoi_id = tournois()[0]["id"]
    autres_avant = {t["id"]: list(t["equipes_ids"])
                    for t in tournois() if t["id"] != tournoi_id}

    EquipeService.creer_equipe(payload_valide(tournoi_id=tournoi_id))

    for t in tournois():
        if t["id"] != tournoi_id:
            assert t["equipes_ids"] == autres_avant[t["id"]]


def test_creer_equipe_ids_uniques():
    """Vérifie que deux créations successives reçoivent des ID différents."""
    e1 = EquipeService.creer_equipe(payload_valide(nom="Equipe A", joueurs_ids=[JOUEURS_LIBRES[0]]))
    e2 = EquipeService.creer_equipe(payload_valide(nom="Equipe B", joueurs_ids=[JOUEURS_LIBRES[1]]))
    assert e1["id"] != e2["id"]


def test_creer_equipe_tournoi_inexistant():
    """Vérifie qu'un tournoi inconnu est refusé et sans effet."""
    avant = len(equipes())
    with pytest.raises(ValueError, match="n'existe pas"):
        EquipeService.creer_equipe(payload_valide(tournoi_id=999))
    assert len(equipes()) == avant


def test_creer_equipe_capitaine_premier_joueur():
    """Vérifie que le capitaine enregistré est le premier joueur de la liste."""
    equipe = EquipeService.creer_equipe(
        payload_valide(joueurs_ids=[JOUEURS_LIBRES[1], JOUEURS_LIBRES[0]])
    )
    assert equipe["capitaine_id"] == JOUEURS_LIBRES[1]
    assert equipe["joueurs_ids"] == [JOUEURS_LIBRES[1], JOUEURS_LIBRES[0]]


def test_creer_equipe_sans_joueur():
    """Vérifie qu'une équipe sans joueur (donc sans capitaine) est refusée et sans effet."""
    avant = len(equipes())
    with pytest.raises(ValueError, match="au moins un joueur"):
        EquipeService.creer_equipe(payload_valide(joueurs_ids=[]))
    assert len(equipes()) == avant


def test_creer_equipe_administrateur_refuse():
    """Vérifie qu'un administrateur ne peut pas faire partie d'une équipe."""
    avant = len(equipes())
    with pytest.raises(ValueError, match="administrateur"):
        EquipeService.creer_equipe(payload_valide(joueurs_ids=[JOUEURS_LIBRES[0], ADMIN_ID]))
    assert len(equipes()) == avant


def test_creer_equipe_nom_deja_pris_dans_le_tournoi():
    """Vérifie qu'un nom déjà utilisé dans le même tournoi est refusé et sans effet."""
    avant = len(equipes())
    with pytest.raises(ValueError, match="nom"):
        EquipeService.creer_equipe(payload_valide(nom=equipes()[0]["nom"]))
    assert len(equipes()) == avant


def test_creer_equipe_joueur_deja_dans_une_equipe_du_tournoi():
    """Vérifie qu'un joueur déjà inscrit dans ce tournoi est refusé, sans effet
    (ni équipe ni membre créés)."""
    avant = len(equipes())
    deja_inscrit = equipes()[0]["joueurs_ids"][0]
    with pytest.raises(ValueError, match="autre équipe"):
        EquipeService.creer_equipe(payload_valide(joueurs_ids=[JOUEURS_LIBRES[0], deja_inscrit]))
    assert len(equipes()) == avant


def test_creer_equipe_joueur_inexistant():
    """Vérifie qu'un joueur qui n'existe pas est refusé et sans effet."""
    avant = len(equipes())
    with pytest.raises(ValueError, match="n'existe pas"):
        EquipeService.creer_equipe(payload_valide(joueurs_ids=[JOUEURS_LIBRES[0], 999]))
    assert len(equipes()) == avant


def test_creer_equipe_joueurs_en_double():
    """Vérifie qu'un joueur listé deux fois est refusé et sans effet."""
    avant = len(equipes())
    with pytest.raises(ValueError):
        EquipeService.creer_equipe(payload_valide(joueurs_ids=[JOUEURS_LIBRES[0], JOUEURS_LIBRES[0]]))
    assert len(equipes()) == avant


def test_creer_equipe_tournoi_id_invalide():
    """Vérifie qu'un tournoi_id qui n'est pas un entier est rejeté par le DTO."""
    with pytest.raises(ValidationError):
        payload_valide(tournoi_id="abc")


def test_creer_equipe_champ_manquant():
    """Vérifie que le nom et le tournoi sont obligatoires dans le DTO de création."""
    with pytest.raises(ValidationError):
        EquipeCreate(tournoi_id=1)
    with pytest.raises(ValidationError):
        EquipeCreate(nom="Sans tournoi")


# ============================================================
# TESTS : CONTRÔLEUR - GET_EQUIPES (GET /equipes)
# ============================================================

def test_controller_get_equipes():
    """Vérifie que le contrôleur renvoie les équipes fournies par le service."""
    resultat = get_equipes()
    assert len(resultat) == len(equipes())
    assert resultat == EquipeService.lister_equipes()


# ============================================================
# TESTS : CONTRÔLEUR - POST_EQUIPE (POST /equipes)
# ============================================================

def test_controller_post_equipe():
    """Vérifie que le contrôleur crée une équipe via le service."""
    avant = len(equipes())

    equipe = post_equipe(payload_valide())

    assert equipe["nom"] == "Les Invincibles"
    assert equipe["tournoi_id"] == tournois()[0]["id"]
    assert equipe in EquipeService.lister_equipes()
    assert len(equipes()) == avant + 1
    assert equipe["id"] in get_tournoi(tournois()[0]["id"])["equipes_ids"]


def test_controller_post_equipe_tournoi_inexistant():
    """Vérifie que le contrôleur transforme l'erreur du service en 400."""
    with pytest.raises(HTTPException) as erreur:
        post_equipe(payload_valide(tournoi_id=999))
    assert erreur.value.status_code == 400
    assert "n'existe pas" in erreur.value.detail


# ============================================================
# TESTS : CONTRÔLEUR - GET_EQUIPE_DETAIL (GET /equipes/{equipe_id})
# ============================================================

def test_controller_get_equipe_detail():
    """Vérifie que le contrôleur renvoie le détail enrichi de l'équipe."""
    equipe_id = equipes()[0]["id"]
    detail = get_equipe_detail(equipe_id, current_user=None)

    assert detail["id"] == equipe_id
    assert len(detail["joueurs"]) == len(equipes()[0]["joueurs_ids"])
    # Visiteur : le chat n'est pas lisible (messages = None)
    assert detail == EquipeService.obtenir_equipe_detail(equipe_id, inclure_messages=False)
    assert detail["messages"] is None


def test_controller_get_equipe_detail_membre_voit_les_messages():
    """Vérifie qu'un membre de l'équipe reçoit les messages du chat."""
    equipe = equipes()[0]
    membre = get_utilisateur(equipe["joueurs_ids"][0])
    detail = get_equipe_detail(equipe["id"], current_user=membre)
    assert detail == EquipeService.obtenir_equipe_detail(equipe["id"], inclure_messages=True)
    assert detail["messages"]


def test_controller_get_equipe_detail_inexistante():
    """Vérifie qu'un ID d'équipe inconnu renvoie une 404."""
    with pytest.raises(HTTPException) as erreur:
        get_equipe_detail(999, current_user=None)
    assert erreur.value.status_code == 404
    assert erreur.value.detail == "Equipe introuvable"


# ============================================================
# BLOC D'EXÉCUTION EN BAS DU FICHIER (Pour lancer le rapport)
# ============================================================
if __name__ == "__main__":
    pytest.main(["-v", __file__])
