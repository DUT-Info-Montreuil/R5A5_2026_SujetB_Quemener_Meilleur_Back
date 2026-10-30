# ============================================================
# DONNÉES FICTIVES
# Aucun SQLite, aucune base de données.
# Tout est stocké simplement dans ces listes Python, partagées
# par tous les services / contrôleurs de l'application.
# ============================================================

jeux = [
    {
        "id": 1,
        "nom": "League of Legends",
        "description": "Jeu de stratégie en équipe",
    },
    {
        "id": 2,
        "nom": "Valorant",
        "description": "Jeu de tir tactique en équipe",
    },
]

utilisateurs = [
    {"id": 1, "login": "alex", "isAdmin": True},
    {"id": 2, "login": "max"},
    {"id": 3, "login": "lina"},
    {"id": 4, "login": "tom"},
    {"id": 5, "login": "sarah"},
    {"id": 6, "login": "nathan"},
    {"id": 7, "login": "emma"},
    {"id": 8, "login": "lucas"},
    {"id": 9, "login": "chloe"},
    {"id": 10, "login": "hugo"},
    {"id": 11, "login": "lea"},
    {"id": 12, "login": "enzo"},
    {"id": 13, "login": "jade"},
    {"id": 14, "login": "noah"},
    {"id": 15, "login": "zoe"},
    {"id": 16, "login": "yanis"},
]

# Une seule entité "Equipe".
# Le même nom peut donc exister dans plusieurs tournois.
equipes = [
    # Tournoi 1
    {
        "id": 1,
        "nom": "Les Dragons",
        "tournoi_id": 1,
        "joueurs_ids": [1, 2, 3, 4],
    },
    {
        "id": 2,
        "nom": "Les Tigres",
        "tournoi_id": 1,
        "joueurs_ids": [5, 6, 7, 8],
    },
    {
        "id": 3,
        "nom": "Les Phoenix",
        "tournoi_id": 1,
        "joueurs_ids": [9, 10, 11, 12],
    },
    {
        "id": 4,
        "nom": "Les Loups",
        "tournoi_id": 1,
        "joueurs_ids": [13, 14, 15, 16],
    },

    # Tournoi 2
    {
        "id": 5,
        "nom": "Les Dragons",
        "tournoi_id": 2,
        "joueurs_ids": [1, 5, 9, 13],
    },
    {
        "id": 6,
        "nom": "Les Tigres",
        "tournoi_id": 2,
        "joueurs_ids": [2, 6, 10, 14],
    },
    {
        "id": 7,
        "nom": "Les Phoenix",
        "tournoi_id": 2,
        "joueurs_ids": [3, 7, 11, 15],
    },
    {
        "id": 8,
        "nom": "Les Loups",
        "tournoi_id": 2,
        "joueurs_ids": [4, 8, 12, 16],
    },
]

tournois = [
    {
        "id": 1,
        "nom": "Summer Cup 2026",
        "description": "Tournoi fictif de League of Legends",
        "statut": "FERME",  # inscriptions closes : passer en EN_COURS génère l'arbre
        "jeu_id": 1,
        "petite_finale": True,
        "equipes_ids": [1, 2, 3, 4],
    },
    {
        "id": 2,
        "nom": "Autumn Cup 2026",
        "description": "Tournoi fictif de Valorant",
        "statut": "TERMINE",
        "jeu_id": 2,
        "petite_finale": True,
        "equipes_ids": [5, 6, 7, 8],
    },
]

# Matchs = noeuds de l'arbre d'élimination directe.
#  - round / position : place dans l'arbre (round 1 = premier tour)
#  - equipe1_id / equipe2_id : None tant que l'équipe n'est pas connue
#  - score_* : None tant que le match n'est pas joué (score = manches gagnées)
#  - next_match_id / next_slot : où avance le vainqueur
#  - loser_next_* : où va le perdant (petite finale), sinon None
#  - bye : match à une seule équipe, qualifiée d'office
# Summer Cup (tournoi 1) n'a aucun match : l'arbre est généré au passage EN_COURS.
def _m(id, rnd, pos, e1, e2, s1, s2, win, nxt, slot, lnxt=None, lslot=None, petite=False):
    return {
        "id": id, "tournoi_id": 2, "round": rnd, "position": pos,
        "equipe1_id": e1, "equipe2_id": e2,
        "score_equipe1": s1, "score_equipe2": s2, "vainqueur_id": win,
        "next_match_id": nxt, "next_slot": slot,
        "loser_next_match_id": lnxt, "loser_next_slot": lslot,
        "petite_finale": petite, "bye": False,
    }


matchs = [
    # Autumn Cup : demi-finales, finale, petite finale
    _m(1, 1, 0, 5, 8, 2, 1, 5, 3, 1, 4, 1),
    _m(2, 1, 1, 6, 7, 2, 0, 6, 3, 2, 4, 2),
    _m(3, 2, 0, 5, 6, 3, 1, 5, None, None),
    _m(4, 2, 1, 8, 7, 2, 0, 8, None, None, petite=True),
]

messages = [
    {"id": 1, "message": "Bienvenue dans l'équipe !", "utilisateur_id": 1, "equipe_id": 1},
    {"id": 2, "message": "Bon tournoi à tous !", "utilisateur_id": 5, "equipe_id": 2},
    {"id": 3, "message": "On est prêts !", "utilisateur_id": 9, "equipe_id": 3},
    {"id": 4, "message": "Rendez-vous demain matin.", "utilisateur_id": 13, "equipe_id": 4},
    {"id": 5, "message": "Bienvenue pour le deuxième tournoi !", "utilisateur_id": 1, "equipe_id": 5},
]

demandes = [
    {"id": 1, "equipe_id": 2, "utilisateur_id": 2, "statut": "EN_ATTENTE"},
    {"id": 2, "equipe_id": 4, "utilisateur_id": 3, "statut": "EN_ATTENTE"},
    {"id": 3, "equipe_id": 3, "utilisateur_id": 4, "statut": "REFUSEE"},
]

def get_demande(demande_id: int):
    return next((d for d in demandes if d["id"] == demande_id), None)

def get_equipe(equipe_id: int):
    return next((e for e in equipes if e["id"] == equipe_id), None)


def get_utilisateur(utilisateur_id: int):
    return next((u for u in utilisateurs if u["id"] == utilisateur_id), None)


def get_tournoi(tournoi_id: int):
    return next((t for t in tournois if t["id"] == tournoi_id), None)


def get_jeu(jeu_id: int):
    return next((j for j in jeux if j["id"] == jeu_id), None)


def get_match(match_id: int):
    return next((m for m in matchs if m["id"] == match_id), None)
