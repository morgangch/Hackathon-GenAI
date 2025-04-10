-- 1. TABLE : Characters
CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,          -- Ex: 'Kadoc'
    description TEXT NOT NULL           -- Ex: 'Comprend mal'
);

-- 2. TABLE : Character Traits (optionnelle mais utile si traits séparables ou multiples)
CREATE TABLE IF NOT EXISTS character_traits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    trait TEXT NOT NULL,                -- Ex: 'Distrait', 'Logique étrange'
    FOREIGN KEY(character_id) REFERENCES characters(id)
);

-- 3. TABLE : Sessions
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,              -- Peut être pseudo ou id discord, ou juste 'anonyme'
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    current_topic TEXT                  -- Dernière notion traitée : ex "Mitose", "TCP/IP", etc.
);

-- 4. TABLE : Messages
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    character_id INTEGER,               -- NULL si c'est un message de l'utilisateur
    sender TEXT NOT NULL,               -- 'user' ou 'bot'
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES sessions(id),
    FOREIGN KEY(character_id) REFERENCES characters(id)
);
