import uvicorn
from fastapi import FastAPI
from controllers.equipe_controller import router as equipe_router

app = FastAPI(
    title="Bouchon API - Équipes",
    description="API préparée pour une intégration future avec une base de données.",
    version="1.0.0",
)

app.include_router(equipe_router)

# Ajout pour lancer le serveur au démarrage du script
if __name__ == "__main__":
    uvicorn.run("luncher:app", host="127.0.0.1", port=8000, reload=True)