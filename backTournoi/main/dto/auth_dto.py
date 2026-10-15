from pydantic import BaseModel, Field


class RegisterPayload(BaseModel):
    login: str = Field(min_length=3, max_length=50)
    # aligné sur UtilisateurCreate.mdp (max 50)
    mot_de_passe: str = Field(min_length=8, max_length=50)
    is_admin: bool = False  # déclaratif pour l'instant, à sécuriser plus tard


class LoginPayload(BaseModel):
    login: str
    mot_de_passe: str


class AuthUserOut(BaseModel):
    """Vue publique d'un utilisateur : ne contient JAMAIS le hash."""
    id: int
    login: str
    is_admin: bool


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    utilisateur: AuthUserOut