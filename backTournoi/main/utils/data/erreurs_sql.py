import sqlite3


def erreur_metier(erreur: sqlite3.IntegrityError) -> ValueError:
    """Traduit une violation de contrainte SQLite en ValueError (les controllers
    la transforment déjà en HTTP 400)."""
    message = str(erreur)
    if "equipes.tournoi_id" in message and "equipes.nom" in message:
        return ValueError("Une équipe portant ce nom existe déjà dans ce tournoi.")
    if "membres.tournoi_id" in message and "membres.utilisateur_id" in message:
        return ValueError("Un joueur fait déjà partie d'une autre équipe de ce tournoi.")
    if "membres.equipe_id" in message and "membres.utilisateur_id" in message:
        return ValueError("Un joueur apparaît plusieurs fois dans l'équipe.")
    if "utilisateurs.login" in message:
        return ValueError("Ce login existe déjà.")
    if "FOREIGN KEY" in message:
        return ValueError("Référence invalide : un des éléments liés n'existe pas.")
    return ValueError(f"Contrainte de la base non respectée : {message}")
