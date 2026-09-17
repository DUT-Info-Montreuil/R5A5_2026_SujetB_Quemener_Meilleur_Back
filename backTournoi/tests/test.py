
from fastapi import FastAPI

app = FastAPI(
    title="Bouchon API - Tournois",
    description="Données fictives en mémoire pour tester le front sans base de données.",
    version="1.0.0",
)

# ============================================================
# DONNÉES FICTIVES
# Aucun SQLite, aucune base de données.
# Tout est stocké simplement dans ces listes Python.
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
        "date_debut": "2026-09-20",
        "date_fin": "2026-09-21",
        "jeu_id": 1,
        "equipes_ids": [1, 2, 3, 4],
    },
    {
        "id": 2,
        "nom": "Autumn Cup 2026",
        "description": "Tournoi fictif de Valorant",
        "date_debut": "2026-10-10",
        "date_fin": "2026-10-11",
        "jeu_id": 2,
        "equipes_ids": [5, 6, 7, 8],
    },
]

# equipe1_id correspond toujours à score_equipe1
# equipe2_id correspond toujours à score_equipe2
matchs = [
    # Summer Cup
    {
        "id": 1,
        "date": "2026-09-20T10:00:00",
        "equipe1_id": 1,
        "equipe2_id": 2,
        "score_equipe1": 3,
        "score_equipe2": 1,
    },
    {
        "id": 2,
        "date": "2026-09-20T11:00:00",
        "equipe1_id": 3,
        "equipe2_id": 4,
        "score_equipe1": 2,
        "score_equipe2": 2,
    },
    {
        "id": 3,
        "date": "2026-09-20T14:00:00",
        "equipe1_id": 1,
        "equipe2_id": 3,
        "score_equipe1": 1,
        "score_equipe2": 2,
    },
    {
        "id": 4,
        "date": "2026-09-20T15:00:00",
        "equipe1_id": 2,
        "equipe2_id": 4,
        "score_equipe1": 4,
        "score_equipe2": 0,
    },
    {
        "id": 5,
        "date": "2026-09-21T10:00:00",
        "equipe1_id": 1,
        "equipe2_id": 4,
        "score_equipe1": 2,
        "score_equipe2": 1,
    },
    {
        "id": 6,
        "date": "2026-09-21T11:00:00",
        "equipe1_id": 2,
        "equipe2_id": 3,
        "score_equipe1": 0,
        "score_equipe2": 3,
    },

    # Autumn Cup
    {
        "id": 7,
        "date": "2026-10-10T10:00:00",
        "equipe1_id": 5,
        "equipe2_id": 6,
        "score_equipe1": 5,
        "score_equipe2": 2,
    },
    {
        "id": 8,
        "date": "2026-10-10T11:00:00",
        "equipe1_id": 7,
        "equipe2_id": 8,
        "score_equipe1": 1,
        "score_equipe2": 3,
    },
    {
        "id": 9,
        "date": "2026-10-10T14:00:00",
        "equipe1_id": 5,
        "equipe2_id": 7,
        "score_equipe1": 2,
        "score_equipe2": 2,
    },
    {
        "id": 10,
        "date": "2026-10-10T15:00:00",
        "equipe1_id": 6,
        "equipe2_id": 8,
        "score_equipe1": 3,
        "score_equipe2": 1,
    },
    {
        "id": 11,
        "date": "2026-10-11T10:00:00",
        "equipe1_id": 5,
        "equipe2_id": 8,
        "score_equipe1": 0,
        "score_equipe2": 1,
    },
    {
        "id": 12,
        "date": "2026-10-11T11:00:00",
        "equipe1_id": 6,
        "equipe2_id": 7,
        "score_equipe1": 4,
        "score_equipe2": 2,
    },
]

messages = [
    {
        "id": 1,
        "message": "Bienvenue dans l'équipe !",
        "date": "2026-09-19T18:00:00",
        "utilisateur_id": 1,
        "equipe_id": 1,
    },
    {
        "id": 2,
        "message": "Bon tournoi à tous !",
        "date": "2026-09-19T18:05:00",
        "utilisateur_id": 5,
        "equipe_id": 2,
    },
    {
        "id": 3,
        "message": "On est prêts !",
        "date": "2026-09-19T18:10:00",
        "utilisateur_id": 9,
        "equipe_id": 3,
    },
    {
        "id": 4,
        "message": "Rendez-vous demain matin.",
        "date": "2026-09-19T18:15:00",
        "utilisateur_id": 13,
        "equipe_id": 4,
    },
    {
        "id": 5,
        "message": "Bienvenue pour le deuxième tournoi !",
        "date": "2026-10-09T18:00:00",
        "utilisateur_id": 1,
        "equipe_id": 5,
    },
]


def get_equipe(equipe_id: int):
    return next((e for e in equipes if e["id"] == equipe_id), None)


def get_utilisateur(utilisateur_id: int):
    return next((u for u in utilisateurs if u["id"] == utilisateur_id), None)


def get_tournoi(tournoi_id: int):
    return next((t for t in tournois if t["id"] == tournoi_id), None)


def get_jeu(jeu_id: int):
    return next((j for j in jeux if j["id"] == jeu_id), None)


@app.get("/")
def accueil():
    return {
        "message": "Bouchon API Tournois",
        "mode": "donnees fictives en memoire",
        "docs": "/docs",
    }


@app.get("/tournois")
def liste_tournois():
    return tournois


@app.get("/tournois/{tournoi_id}")
def detail_tournoi(tournoi_id: int):
    tournoi = get_tournoi(tournoi_id)

    if not tournoi:
        return {"error": "Tournoi introuvable"}

    jeu = get_jeu(tournoi["jeu_id"])
    equipes_tournoi = [
        e for e in equipes if e["id"] in tournoi["equipes_ids"]
    ]

    return {
        **tournoi,
        "jeu": jeu,
        "equipes": equipes_tournoi,
        "matchs": [
            m for m in matchs
            if m["equipe1_id"] in tournoi["equipes_ids"]
            and m["equipe2_id"] in tournoi["equipes_ids"]
        ],
    }


@app.get("/equipes")
def liste_equipes():
    return equipes


@app.get("/equipes/{equipe_id}")
def detail_equipe(equipe_id: int):
    equipe = get_equipe(equipe_id)

    if not equipe:
        return {"error": "Equipe introuvable"}

    joueurs = [
        get_utilisateur(uid)
        for uid in equipe["joueurs_ids"]
    ]

    tournoi = get_tournoi(equipe["tournoi_id"])

    equipe_matchs = [
        m for m in matchs
        if m["equipe1_id"] == equipe_id
        or m["equipe2_id"] == equipe_id
    ]

    equipe_messages = [
        m for m in messages
        if m["equipe_id"] == equipe_id
    ]

    return {
        **equipe,
        "tournoi": tournoi,
        "joueurs": joueurs,
        "matchs": equipe_matchs,
        "messages": equipe_messages,
    }


@app.get("/matchs")
def liste_matchs():
    resultat = []

    for match in matchs:
        equipe1 = get_equipe(match["equipe1_id"])
        equipe2 = get_equipe(match["equipe2_id"])

        resultat.append({
            "id": match["id"],
            "date": match["date"],
            "equipe1": {
                "id": equipe1["id"],
                "nom": equipe1["nom"],
                "score": match["score_equipe1"],
            },
            "equipe2": {
                "id": equipe2["id"],
                "nom": equipe2["nom"],
                "score": match["score_equipe2"],
            },
        })

    return resultat


@app.get("/utilisateurs")
def liste_utilisateurs():
    return utilisateurs


@app.get("/messages")
def liste_messages():
    return messages
