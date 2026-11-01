# 🏆 Gestion de tournois — API Back-end

API REST de gestion de tournois d'e-sport (équipes, demandes d'adhésion, messagerie d'équipe, arbre d'élimination directe avec petite finale optionnelle).
Projet réalisé dans le cadre du **BUT Informatique de Montreuil** (R5.A.05 — 2026, sujet B).

Ce dépôt contient uniquement le **back-end**. L'interface web correspondante est dans le dépôt **Front-end** : <https://github.com/DUT-Info-Montreuil/R5A5_2026_SujetB_Quemener_Meilleur_Front>

---

## 📚 Technologies utilisées

| Technologie | Version testée | Rôle |
|---|---|---|
| [Python](https://www.python.org/) | 3.11 | Langage |
| [FastAPI](https://fastapi.tiangolo.com/) | 0.162.0 | Framework web / API REST |
| [Uvicorn](https://www.uvicorn.org/) | 0.54.0 | Serveur ASGI |
| [Pydantic](https://docs.pydantic.dev/) | 2.14.2 | Validation des données (DTO) |
| SQLite (`sqlite3`) | module natif de Python | Base de données (sans ORM, SQL écrit à la main) |
| [PyJWT](https://pyjwt.readthedocs.io/) | 2.15.1 | Authentification par jeton JWT (HS256, validité 8 h) |
| [bcrypt](https://pypi.org/project/bcrypt/) | 5.0.0 | Hachage des mots de passe |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | 1.2.4 | Chargement des variables d'environnement (`.env`) |
| [pytest](https://docs.pytest.org/) | 9.2.0 | Tests |
| [httpx](https://www.python-httpx.org/) | 0.28.1 | Client HTTP (requis par FastAPI pour les tests) |

> Les versions ci-dessus sont celles installées et vérifiées pour ce README. Elles sont regroupées dans `requirements.txt`.

---

## 🗂️ Architecture

```
backTournoi/
├── main/
│   ├── launcher.py          # Point d'entrée FastAPI (app, CORS, routeurs)
│   ├── .env.example         # Modèle de configuration
│   ├── controllers/         # Routes HTTP (auth, tournois, équipes, matchs, messages, demandes, utilisateurs)
│   ├── services/            # Logique métier (dont génération de l'arbre : bracket_service)
│   ├── repo/                # Accès aux données (SQL)
│   ├── dto/                 # Schémas Pydantic (entrées / sorties)
│   └── utils/
│       ├── security.py      # JWT + bcrypt
│       └── data/            # schema.sql, connexion SQLite, transactions
└── tests/                   # Tests pytest
```

---

## ⚙️ Installation

### Prérequis
- **Python 3.11**
- **Git**

### 1. Récupérer le projet
```bash
git clone https://github.com/DUT-Info-Montreuil/R5A5_2026_SujetB_Quemener_Meilleur_Back.git
cd R5A5_2026_SujetB_Quemener_Meilleur_Back
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```
Si la commande `pip` n'est pas reconnue, utilisez `python -m pip install -r requirements.txt`.

### 3. Configurer l'environnement
Copiez le modèle puis renseignez votre propre clé secrète :
```bash
# Linux / macOS
cp backTournoi/main/.env.example backTournoi/main/.env
# Windows
copy backTournoi\main\.env.example backTournoi\main\.env
```

Contenu du fichier `backTournoi/main/.env` :
```env
JWT_SECRET_KEY=<une_longue_chaine_aleatoire>
```
Générez une clé avec : `openssl rand -hex 32` (ou `python -c "import secrets; print(secrets.token_hex(32))"`).

---

## ▶️ Lancer l'application

Depuis la **racine du dépôt** :

```bash
# Linux / macOS
PYTHONPATH=. python -m uvicorn launcher:app --app-dir backTournoi/main --reload

# Windows (PowerShell)
$env:PYTHONPATH = "."
python -m uvicorn launcher:app --app-dir backTournoi/main --reload
```

- API : <http://127.0.0.1:8000>
- Documentation interactive Swagger : <http://127.0.0.1:8000/docs>
- Documentation ReDoc : <http://127.0.0.1:8000/redoc>

Au premier démarrage, le fichier de base de données `backTournoi/main/utils/data/tournoi.db` est **créé automatiquement** avec toutes ses tables (aucune migration à lancer).

### Compte administrateur par défaut
| Login | Mot de passe |
|---|---|
| `admin` | `admindefou` |

> ⚠️ À changer (ou supprimer) avant toute mise en production.

### Front-end
L'API est conçue pour fonctionner avec le front-end React du projet :
<https://github.com/DUT-Info-Montreuil/R5A5_2026_SujetB_Quemener_Meilleur_Front>

Le front se lance avec `npm run dev` sur <http://localhost:5173> (voir son README) et appelle l'API sur `http://localhost:8000`. Le CORS autorise **uniquement** `http://localhost:5173` : pour un autre port ou domaine, modifiez `allow_origins` dans `backTournoi/main/launcher.py`.

---

## 🚀 Utiliser l'application

### Authentification
1. **Créer un compte** : `POST /auth/register` avec `{"login": "...", "mot_de_passe": "..."}` (login 3–50 car., mot de passe 8–50 car.). Le compte créé est toujours non-administrateur.
2. **Se connecter** : `POST /auth/login` avec `{"login": "...", "mot_de_passe": "..."}` → renvoie un `access_token`.
3. **Envoyer le jeton** dans l'en-tête `Authorization: Bearer <access_token>` pour les routes protégées.
4. Dans Swagger (`/docs`), cliquez sur le bouton **Authorize** et collez le jeton.

`GET /auth/me` renvoie l'utilisateur connecté.

### Rôles et droits

| Ressource | Lecture | Écriture |
|---|---|---|
| `/tournois` | Publique | Admin (création, modification, changement de statut) |
| `/matchs` | Publique | Admin (saisie des scores) |
| `/equipes` | Publique | Utilisateur connecté **non-admin** (création) |
| `/demandes` | Connecté | Non-admin (demander à rejoindre une équipe, accepter / refuser) |
| `/messages` | Connecté | Connecté (membre de l'équipe uniquement) |
| `/utilisateurs` | Connecté | Admin (création) ; modification via `PATCH` |

### Cycle de vie d'un tournoi
Statuts : `OUVERT` → `FERME` → `EN_COURS` → `TERMINE`

1. L'admin crée un tournoi (`POST /tournois/`), éventuellement avec petite finale.
2. Les joueurs créent des équipes (`POST /equipes/`) et envoient des demandes d'adhésion (`POST /demandes/`) ; le **capitaine** de l'équipe les accepte ou refuse (`PATCH /demandes/{id}/accepter` ou `/refuser`). Un joueur ne peut être que dans **une équipe par tournoi**.
3. L'admin ferme les inscriptions (`FERME`), puis passe le tournoi à `EN_COURS` (`PATCH /tournois/{id}`) : **l'arbre d'élimination directe est généré automatiquement**.
4. L'admin saisit les scores (`PATCH /matchs/{id}`) : le vainqueur avance dans l'arbre (et le perdant des demi-finales vers la petite finale).
5. Consultation de l'arbre : `GET /tournois/{id}/arbre`.
6. Les membres d'une équipe échangent via `/messages`.

### Principales routes

| Méthode | Route | Description |
|---|---|---|
| POST | `/auth/register`, `/auth/login` | Inscription / connexion |
| GET | `/auth/me` | Utilisateur courant |
| GET / POST | `/tournois/` | Lister / créer |
| GET / PATCH | `/tournois/{id}` | Détail / modifier |
| GET | `/tournois/{id}/arbre` | Arbre des matchs |
| GET | `/matchs/`, `/matchs/{id}` | Consulter les matchs |
| PATCH | `/matchs/{id}` | Saisir un score (admin) |
| GET / POST | `/equipes/` | Lister / créer |
| GET | `/equipes/{id}` | Détail d'une équipe |
| GET / POST | `/demandes/` | Lister / créer une demande |
| PATCH | `/demandes/{id}/accepter` · `/refuser` | Traiter une demande |
| GET / POST | `/messages/` | Lister / envoyer |
| GET / POST | `/utilisateurs/` | Lister / créer (admin) |
| GET / PATCH | `/utilisateurs/{id}` | Détail / modifier |

Exemple avec `curl` :
```bash
# Connexion
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login": "admin", "mot_de_passe": "admindefou"}'

# Requête authentifiée
curl http://127.0.0.1:8000/utilisateurs/ -H "Authorization: Bearer <access_token>"
```

---

## 🧪 Tests

```bash
pytest
```
Chaque test s'exécute sur une base SQLite temporaire : la vraie base n'est jamais touchée.

---

## 📄 Licence

Distribué sous licence **MIT** — voir le fichier [LICENSE](LICENSE).
