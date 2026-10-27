import random
from typing import Optional

from ..utils.data.data import matchs, get_tournoi, get_equipe


def _ordre_seeds(taille: int) -> list:
    """Ordre standard d'un arbre : pour 8 -> [1, 8, 4, 5, 2, 7, 3, 6].
    Les paires sont (1,8) (4,5) (2,7) (3,6) : les 'byes' (seeds > nb d'équipes)
    tombent toujours face aux premiers seeds, jamais deux byes ensemble."""
    ordre = [1]
    while len(ordre) < taille:
        n = len(ordre) * 2
        ordre = [x for s in ordre for x in (s, n + 1 - s)]
    return ordre


def _nouveau_match(match_id: int, tournoi_id: int, rnd: int, pos: int, petite: bool = False) -> dict:
    return {
        "id": match_id,
        "tournoi_id": tournoi_id,
        "round": rnd,
        "position": pos,
        "equipe1_id": None,
        "equipe2_id": None,
        "score_equipe1": None,
        "score_equipe2": None,
        "vainqueur_id": None,
        "next_match_id": None,
        "next_slot": None,
        "loser_next_match_id": None,
        "loser_next_slot": None,
        "petite_finale": petite,
        "bye": False,
    }


def _titre_round(rnd: int, total: int) -> str:
    reste = total - rnd
    return {0: "Finale", 1: "Demi-finales", 2: "Quarts de finale", 3: "8es de finale"}.get(
        reste, f"Tour {rnd}"
    )


class BracketService:
    """Génération et lecture de l'arbre d'élimination directe."""

    @staticmethod
    def generer(tournoi: dict) -> list:
        """Génère (une seule fois) tous les matchs de l'arbre, tirage aléatoire.
        Lève ValueError si impossible. N'écrit dans `matchs` qu'en cas de succès."""
        tournoi_id = tournoi["id"]
        equipes_ids = list(tournoi["equipes_ids"])
        n = len(equipes_ids)

        if n < 2:
            raise ValueError("Il faut au moins 2 équipes pour démarrer le tournoi.")
        if any(m["tournoi_id"] == tournoi_id for m in matchs):
            raise ValueError("L'arbre de ce tournoi a déjà été généré.")

        random.shuffle(equipes_ids)

        taille = 1 << (n - 1).bit_length()          # puissance de 2 >= n
        nb_rounds = taille.bit_length() - 1
        next_id = max((m["id"] for m in matchs), default=0) + 1

        # Squelette : arbre[r][p]
        arbre = []
        for r in range(nb_rounds):
            ligne = []
            for p in range(taille >> (r + 1)):
                ligne.append(_nouveau_match(next_id, tournoi_id, r + 1, p))
                next_id += 1
            arbre.append(ligne)

        # Chaînage : le vainqueur du match p va dans le match p//2 du tour suivant
        for r in range(nb_rounds - 1):
            for p, m in enumerate(arbre[r]):
                parent = arbre[r + 1][p // 2]
                m["next_match_id"] = parent["id"]
                m["next_slot"] = 1 if p % 2 == 0 else 2

        # Petite finale : perdants des demi-finales (impossible si une demi est un bye)
        petite = None
        if tournoi.get("petite_finale") and n >= 4:
            petite = _nouveau_match(next_id, tournoi_id, nb_rounds, 1, petite=True)
            for p, m in enumerate(arbre[nb_rounds - 2]):
                m["loser_next_match_id"] = petite["id"]
                m["loser_next_slot"] = 1 if p % 2 == 0 else 2

        # Premier tour : placement des équipes, byes qualifiés d'office
        places = [equipes_ids[s - 1] if s <= n else None for s in _ordre_seeds(taille)]
        parents = {m["id"]: m for ligne in arbre for m in ligne}
        for p, m in enumerate(arbre[0]):
            e1, e2 = places[2 * p], places[2 * p + 1]
            m["equipe1_id"], m["equipe2_id"] = e1, e2
            if e2 is None:  # bye : e1 est toujours renseignée
                m["bye"] = True
                m["vainqueur_id"] = e1
                if m["next_match_id"] is not None:
                    parent = parents[m["next_match_id"]]
                    parent[f"equipe{m['next_slot']}_id"] = e1

        tous = [m for ligne in arbre for m in ligne]
        if petite:
            tous.append(petite)
        matchs.extend(tous)
        return tous

    @staticmethod
    def arbre(tournoi_id: int) -> Optional[dict]:
        """Arbre structuré par tours, prêt pour l'affichage. rounds=[] si non généré."""
        if not get_tournoi(tournoi_id):
            return None

        def nom(eid):
            e = get_equipe(eid) if eid is not None else None
            return e["nom"] if e else None

        def enrichi(m):
            return {**m, "equipe1_nom": nom(m["equipe1_id"]), "equipe2_nom": nom(m["equipe2_id"])}

        ms = [m for m in matchs if m["tournoi_id"] == tournoi_id]
        principaux = [m for m in ms if not m["petite_finale"]]
        nb_rounds = max((m["round"] for m in principaux), default=0)

        rounds = []
        for r in range(1, nb_rounds + 1):
            ligne = sorted((m for m in principaux if m["round"] == r), key=lambda m: m["position"])
            rounds.append({"round": r, "titre": _titre_round(r, nb_rounds), "matchs": [enrichi(m) for m in ligne]})

        petite = next((m for m in ms if m["petite_finale"]), None)
        return {
            "tournoi_id": tournoi_id,
            "rounds": rounds,
            "petite_finale": enrichi(petite) if petite else None,
        }
