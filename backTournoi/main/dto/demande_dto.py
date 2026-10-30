from pydantic import BaseModel


class DemandeCreate(BaseModel):
    equipe_id: int
    utilisateur_id: int


class DemandeOut(BaseModel):
    id: int
    equipe_id: int
    utilisateur_id: int
    statut: str  # "EN_ATTENTE" | "ACCEPTEE" | "REFUSEE"
