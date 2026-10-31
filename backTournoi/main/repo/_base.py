"""Utilitaires communs : conversion des lignes SQLite en dictionnaires, quel que
soit le row_factory de la connexion."""


def un(curseur):
    """Première ligne du curseur sous forme de dict, ou None."""
    ligne = curseur.fetchone()
    if ligne is None:
        return None
    return dict(zip([c[0] for c in curseur.description], ligne))


def tous(curseur):
    """Toutes les lignes du curseur sous forme de liste de dicts."""
    colonnes = [c[0] for c in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]
