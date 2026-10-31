-- ============================================================
-- Schéma SQLite de l'application de tournois.
-- Exécuté à chaque démarrage : tout est en IF NOT EXISTS.
-- Aucune suppression prévue : ON DELETE RESTRICT partout.
-- Booléens stockés en INTEGER (0 / 1). Textes sensibles à la casse
-- (collation BINARY par défaut de SQLite).
-- ============================================================

CREATE TABLE IF NOT EXISTS utilisateurs (
    id        INTEGER PRIMARY KEY,
    login     TEXT    NOT NULL UNIQUE CHECK (length(login) BETWEEN 1 AND 50),
    mdp       TEXT    NOT NULL CHECK (length(mdp) >= 1),
    is_admin  INTEGER NOT NULL DEFAULT 0 CHECK (is_admin IN (0, 1))
);

CREATE TABLE IF NOT EXISTS tournois (
    id             INTEGER PRIMARY KEY,
    nom            TEXT    NOT NULL CHECK (length(nom) BETWEEN 1 AND 50),
    description    TEXT,
    statut         TEXT    NOT NULL DEFAULT 'OUVERT'
                           CHECK (statut IN ('OUVERT', 'FERME', 'EN_COURS', 'TERMINE')),
    petite_finale  INTEGER NOT NULL DEFAULT 0 CHECK (petite_finale IN (0, 1))
);

-- Le capitaine doit être membre de l'équipe : FK composite vers `membres`,
-- différée (vérifiée au COMMIT) car l'équipe est insérée avant ses membres.
CREATE TABLE IF NOT EXISTS equipes (
    id            INTEGER PRIMARY KEY,
    nom           TEXT    NOT NULL CHECK (length(nom) >= 1),
    tournoi_id    INTEGER NOT NULL REFERENCES tournois(id) ON DELETE RESTRICT,
    capitaine_id  INTEGER NOT NULL,
    UNIQUE (tournoi_id, nom),
    UNIQUE (id, tournoi_id),
    FOREIGN KEY (id, capitaine_id) REFERENCES membres(equipe_id, utilisateur_id)
        ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED
);

-- Association Utilisateur <-> Equipe. `tournoi_id` est copié ici pour imposer
-- « une seule équipe par tournoi et par utilisateur ».
CREATE TABLE IF NOT EXISTS membres (
    equipe_id       INTEGER NOT NULL,
    utilisateur_id  INTEGER NOT NULL REFERENCES utilisateurs(id) ON DELETE RESTRICT,
    tournoi_id      INTEGER NOT NULL,
    PRIMARY KEY (equipe_id, utilisateur_id),
    UNIQUE (tournoi_id, utilisateur_id),
    FOREIGN KEY (equipe_id, tournoi_id) REFERENCES equipes(id, tournoi_id)
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS matchs (
    id                   INTEGER PRIMARY KEY,
    tournoi_id           INTEGER NOT NULL REFERENCES tournois(id) ON DELETE RESTRICT,
    round                INTEGER NOT NULL CHECK (round >= 1),
    position             INTEGER NOT NULL CHECK (position >= 0),
    equipe1_id           INTEGER,
    equipe2_id           INTEGER,
    score_equipe1        INTEGER CHECK (score_equipe1 >= 0),
    score_equipe2        INTEGER CHECK (score_equipe2 >= 0),
    vainqueur_id         INTEGER,
    next_match_id        INTEGER REFERENCES matchs(id) ON DELETE RESTRICT
                                 DEFERRABLE INITIALLY DEFERRED,
    next_slot            INTEGER CHECK (next_slot IN (1, 2)),
    loser_next_match_id  INTEGER REFERENCES matchs(id) ON DELETE RESTRICT
                                 DEFERRABLE INITIALLY DEFERRED,
    loser_next_slot      INTEGER CHECK (loser_next_slot IN (1, 2)),
    petite_finale        INTEGER NOT NULL DEFAULT 0 CHECK (petite_finale IN (0, 1)),
    bye                  INTEGER NOT NULL DEFAULT 0 CHECK (bye IN (0, 1)),

    UNIQUE (tournoi_id, round, position, petite_finale),

    -- Les équipes et le vainqueur appartiennent au tournoi du match
    -- (une colonne NULL n'est pas vérifiée : adversaire pas encore connu).
    FOREIGN KEY (equipe1_id, tournoi_id)   REFERENCES equipes(id, tournoi_id) ON DELETE RESTRICT,
    FOREIGN KEY (equipe2_id, tournoi_id)   REFERENCES equipes(id, tournoi_id) ON DELETE RESTRICT,
    FOREIGN KEY (vainqueur_id, tournoi_id) REFERENCES equipes(id, tournoi_id) ON DELETE RESTRICT,

    CHECK (equipe1_id IS NULL OR equipe2_id IS NULL OR equipe1_id <> equipe2_id),
    -- Le vainqueur est l'une des deux équipes (COALESCE : un NULL ferait passer le CHECK)
    CHECK (vainqueur_id IS NULL
           OR COALESCE(vainqueur_id = equipe1_id, 0)
           OR COALESCE(vainqueur_id = equipe2_id, 0)),
    -- Scores renseignés ensemble, jamais égaux (élimination directe)
    CHECK ((score_equipe1 IS NULL) = (score_equipe2 IS NULL)),
    CHECK (score_equipe1 IS NULL OR score_equipe1 <> score_equipe2),
    -- Destination et emplacement renseignés ensemble
    CHECK ((next_match_id IS NULL) = (next_slot IS NULL)),
    CHECK ((loser_next_match_id IS NULL) = (loser_next_slot IS NULL))
);

-- L'auteur doit être membre de l'équipe : FK composite vers `membres`.
CREATE TABLE IF NOT EXISTS messages (
    id              INTEGER PRIMARY KEY,
    equipe_id       INTEGER NOT NULL,
    utilisateur_id  INTEGER NOT NULL,
    message         TEXT    NOT NULL CHECK (length(message) BETWEEN 1 AND 500
                                        AND length(trim(message)) > 0),
    FOREIGN KEY (equipe_id, utilisateur_id) REFERENCES membres(equipe_id, utilisateur_id)
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS demandes (
    id              INTEGER PRIMARY KEY,
    equipe_id       INTEGER NOT NULL REFERENCES equipes(id)      ON DELETE RESTRICT,
    utilisateur_id  INTEGER NOT NULL REFERENCES utilisateurs(id) ON DELETE RESTRICT,
    statut          TEXT    NOT NULL DEFAULT 'EN_ATTENTE'
                            CHECK (statut IN ('EN_ATTENTE', 'ACCEPTEE', 'REFUSEE'))
);

-- Index (equipes.tournoi_id, matchs.tournoi_id et membres.equipe_id sont déjà
-- couverts par les index des contraintes UNIQUE / PRIMARY KEY).
CREATE INDEX IF NOT EXISTS idx_membres_utilisateur  ON membres(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_messages_equipe      ON messages(equipe_id);
CREATE INDEX IF NOT EXISTS idx_messages_utilisateur ON messages(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_demandes_equipe      ON demandes(equipe_id);
CREATE INDEX IF NOT EXISTS idx_demandes_utilisateur ON demandes(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_matchs_equipe1       ON matchs(equipe1_id);
CREATE INDEX IF NOT EXISTS idx_matchs_equipe2       ON matchs(equipe2_id);

INSERT OR IGNORE INTO utilisateurs (login,mdp,is_admin) values ('admin','admindefou', 1);
