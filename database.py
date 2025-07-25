import sqlite3
from datetime import datetime
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'annonces.db')

def get_db_path():
    """Extraire le chemin du fichier de la DATABASE_URL"""
    if DATABASE_URL.startswith('sqlite:///'):
        return DATABASE_URL[10:]  # Supprime 'sqlite:///'
    return DATABASE_URL

def init_database():
    """Initialise la base de données et crée les tables si nécessaire"""
    try:
        db_path = get_db_path()
        # Créer le dossier parent si nécessaire
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS annonces (
                id INTEGER PRIMARY KEY,
                titre TEXT,
                description TEXT,
                prix TEXT,
                type TEXT,
                quartier TEXT,
                surface TEXT,
                chambres INTEGER,
                date_publication DATE,
                date_recuperation DATETIME,
                source TEXT,
                url TEXT UNIQUE
            )
        ''')
        
        conn.commit()
        print(f"✅ Base de données initialisée : {db_path}")
        return True
    except Exception as e:
        print(f"❌ Erreur initialisation base de données : {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()