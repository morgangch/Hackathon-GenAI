import sqlite3
from enum import Enum
from pathlib import Path

class SQLiteManager:
    def __init__(self, db_name):
        self.db_path = Path(db_name)
        self.schema_path = Path(__file__).parent / "scheme.sql"
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
        self.cursor = self.conn.cursor()
        self._initialize_database()

    def reinitialize_database(self):
        """Supprime les tables précédentes et les recrée."""
        self.conn.close()
        if self.db_path.exists():
            self.db_path.unlink()
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._initialize_database()

    def _initialize_database(self):
        """Crée les tables si elles n'existent pas, à partir du fichier schema.sql"""
        with open(self.schema_path, 'r', encoding='utf-8') as schema_file:
            schema_sql = schema_file.read()
            self.cursor.executescript(schema_sql)
            self.conn.commit()

    def insert(self, query, params=()):
        """Insère des données, retourne l'ID de la dernière insertion."""
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor.lastrowid

    def fetch_all(self, query, params=()):
        """Retourne une liste de dictionnaires."""
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def fetch_one(self, query, params=()):
        """Retourne un seul dictionnaire ou None."""
        self.cursor.execute(query, params)
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def execute(self, query, params=()):
        """Exécute une requête sans retour de données (ex: UPDATE ou DELETE)."""
        self.cursor.execute(query, params)
        self.conn.commit()

    def close(self):
        """Ferme proprement la connexion."""
        self.conn.close()