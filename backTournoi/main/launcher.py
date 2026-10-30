import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

from backTournoi.main.services.auth_dependencies import get_current_user
from controllers.auth_controller import router as auth_router
from controllers.equipe_controller import router as equipe_router
from controllers.match_controller import router as match_router
from controllers.tournoi_controller import router as tournoi_router
from controllers.utilisateur_controller import router as utilisateur_router
from controllers.message_controller import router as message_router

app = FastAPI(
    title="Bouchon API",
    description="API préparée pour une intégration future avec une base de données.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # inclut le header Authorization
)

# Routes publiques : inscription, connexion (et /auth/me qui vérifie le jeton lui-même)
app.include_router(auth_router)

# Routeurs MIXTES : lecture publique (consultation des tournois, matchs, équipes),
# écriture protégée. Aucune dépendance globale ici : chaque route d'écriture déclare
# sa propre garde dans son contrôleur (get_current_admin / get_current_non_admin).
# /!\ Toute nouvelle route ajoutée à ces routeurs est PUBLIQUE tant qu'elle n'a pas
#     sa propre dépendance d'authentification.
app.include_router(tournoi_router)
app.include_router(match_router)
app.include_router(equipe_router)

# Routeurs ENTIÈREMENT PRIVÉS : un jeton valide est exigé sur toutes leurs routes
# (refus par défaut).
protected = [Depends(get_current_user)]
app.include_router(utilisateur_router, dependencies=protected)
app.include_router(message_router, dependencies=protected)

# Ajout pour lancer le serveur au démarrage du script
if __name__ == "__main__":
    uvicorn.run("launcher:app", host="127.0.0.1", port=8000, reload=True)