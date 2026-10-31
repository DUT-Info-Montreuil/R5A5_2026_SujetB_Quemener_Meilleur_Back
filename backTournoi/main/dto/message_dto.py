from pydantic import BaseModel, Field, field_validator


class MessageCreate(BaseModel):
    """Données nécessaires pour poster un message dans le chat d'une équipe."""
    equipe_id: int
    utilisateur_id: int
    message: str = Field(..., min_length=1, max_length=500)

    @field_validator("message")
    @classmethod
    def message_non_blanc(cls, valeur: str) -> str:
        """Refuse un message composé uniquement d'espaces."""
        if not valeur.strip():
            raise ValueError("Le contenu du message ne peut pas être vide.")
        return valeur


class MessageOut(BaseModel):
    """Représentation d'un message renvoyée par l'API."""
    id: int
    equipe_id: int
    utilisateur_id: int
    message: str