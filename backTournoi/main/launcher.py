import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    allow_headers=["*"],
)

app.include_router(equipe_router)
app.include_router(match_router)
app.include_router(tournoi_router)

app.include_router(utilisateur_router)
app.include_router(message_router)

# Ajout pour lancer le serveur au démarrage du script
if __name__ == "__main__":
    uvicorn.run("launcher:app", host="127.0.0.1", port=8000, reload=True)