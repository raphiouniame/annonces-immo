import sqlite3
from datetime import datetime
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'annonces.db')

def get_db_path():
    """Extraire le chemin du fichier de la DATABASE_URL"""
    if DATABASE_URL.startswith('sqlite:///'):
        return DATABASE_URL[10:]  # Supprime 'sqlite:///'
    return DATABASE_URL

def get_db_connection():
    """Obtenir une connexion à la base de données"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Pour pouvoir accéder aux colonnes par nom
    return conn

def init_database():
    """Initialise la base de données et crée les tables si nécessaire"""
    try:
        db_path = get_db_path()
        # Créer le dossier parent si nécessaire
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Supprimer l'ancienne table si elle existe (pour la migration)
        cursor.execute('DROP TABLE IF EXISTS annonces_old')
        
        # Vérifier si la colonne contact existe déjà
        cursor.execute("PRAGMA table_info(annonces)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Si la table n'existe pas ou n'a pas la colonne contact, la recréer
        if 'contact_nom' not in columns:
            # Sauvegarder les données existantes si la table existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='annonces'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                cursor.execute('ALTER TABLE annonces RENAME TO annonces_old')
            
            # Créer la nouvelle table avec les colonnes de contact
            cursor.execute('''
                CREATE TABLE annonces (
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
                    url TEXT UNIQUE,
                    contact_nom TEXT,
                    contact_telephone TEXT,
                    contact_email TEXT,
                    contact_whatsapp TEXT
                )
            ''')
            
            # Migrer les données de l'ancienne table si elle existait
            if table_exists:
                cursor.execute('''
                    INSERT INTO annonces (
                        id, titre, description, prix, type, quartier, 
                        surface, chambres, date_publication, date_recuperation, 
                        source, url
                    )
                    SELECT id, titre, description, prix, type, quartier, 
                           surface, chambres, date_publication, date_recuperation, 
                           source, url
                    FROM annonces_old
                ''')
                cursor.execute('DROP TABLE annonces_old')
        
        conn.commit()
        print(f"✅ Base de données initialisée : {db_path}")
        return True
    except Exception as e:
        print(f"❌ Erreur initialisation base de données : {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def save_annonce(annonce):
    """Sauvegarder une annonce dans la base de données"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO annonces (
                id, titre, description, prix, type, quartier, 
                surface, chambres, date_publication, date_recuperation, 
                source, url, contact_nom, contact_telephone, 
                contact_email, contact_whatsapp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            annonce.get('id'),
            annonce.get('titre'),
            annonce.get('description'),
            annonce.get('prix'),
            annonce.get('type'),
            annonce.get('quartier'),
            annonce.get('surface'),
            annonce.get('chambres'),
            annonce.get('date_publication'),
            datetime.now().isoformat(),
            annonce.get('source'),
            annonce.get('url'),
            annonce.get('contact_nom'),
            annonce.get('contact_telephone'),
            annonce.get('contact_email'),
            annonce.get('contact_whatsapp')
        ))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erreur sauvegarde annonce: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def get_annonces_du_jour():
    """Récupérer les annonces du jour"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT * FROM annonces 
            WHERE date_publication = ? 
            ORDER BY date_recuperation DESC
        ''', (today,))
        
        rows = cursor.fetchall()
        annonces = []
        for row in rows:
            annonce = dict(row)
            # Ajouter une image par défaut si pas d'image
            annonce['image'] = 'https://via.placeholder.com/300x200?text=Immobilier'
            annonces.append(annonce)
        
        return annonces
    except Exception as e:
        print(f"Erreur récupération annonces du jour: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

def get_all_annonces():
    """Récupérer toutes les annonces"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM annonces 
            ORDER BY date_recuperation DESC
        ''')
        
        rows = cursor.fetchall()
        annonces = []
        for row in rows:
            annonce = dict(row)
            # Ajouter une image par défaut si pas d'image
            annonce['image'] = 'https://via.placeholder.com/300x200?text=Immobilier'
            annonces.append(annonce)
        
        return annonces
    except Exception as e:
        print(f"Erreur récupération toutes annonces: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

def get_statistiques():
    """Récupérer les statistiques des annonces"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total des annonces
        cursor.execute('SELECT COUNT(*) FROM annonces')
        total_annonces = cursor.fetchone()[0]
        
        # Annonces d'aujourd'hui
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT COUNT(*) FROM annonces WHERE date_publication = ?', (today,))
        annonces_aujourd_hui = cursor.fetchone()[0]
        
        # Ventes
        cursor.execute("SELECT COUNT(*) FROM annonces WHERE type = 'vente'")
        ventes = cursor.fetchone()[0]
        
        # Locations
        cursor.execute("SELECT COUNT(*) FROM annonces WHERE type = 'location'")
        locations = cursor.fetchone()[0]
        
        # Quartiers actifs
        cursor.execute('SELECT COUNT(DISTINCT quartier) FROM annonces')
        quartiers_actifs = cursor.fetchone()[0]
        
        return {
            'total_annonces': total_annonces,
            'annonces_aujourd_hui': annonces_aujourd_hui,
            'ventes': ventes,
            'locations': locations,
            'quartiers_actifs': quartiers_actifs
        }
    except Exception as e:
        print(f"Erreur récupération statistiques: {e}")
        return {
            'total_annonces': 0,
            'annonces_aujourd_hui': 0,
            'ventes': 0,
            'locations': 0,
            'quartiers_actifs': 0
        }
    finally:
        if 'conn' in locals():
            conn.close()