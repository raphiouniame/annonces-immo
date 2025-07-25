import sqlite3
from datetime import datetime
import json

def init_database():
    """Initialise la base de données"""
    conn = sqlite3.connect('annonces.db')
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
    conn.close()

def save_annonce(annonce):
    """Sauvegarde une annonce dans la base de données"""
    conn = sqlite3.connect('annonces.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO annonces 
            (id, titre, description, prix, type, quartier, surface, chambres, 
             date_publication, date_recuperation, source, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            annonce.get('url')
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur sauvegarde annonce: {e}")
        return False
    finally:
        conn.close()

def get_annonces_du_jour():
    """Récupère les annonces du jour depuis la base de données"""
    conn = sqlite3.connect('annonces.db')
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT id, titre, description, prix, type, quartier, surface, 
               chambres, date_publication, source
        FROM annonces 
        WHERE date(date_publication) = date(?)
        ORDER BY date_recuperation DESC
    ''', (today,))
    
    annonces = []
    for row in cursor.fetchall():
        annonces.append({
            'id': row[0],
            'titre': row[1],
            'description': row[2],
            'prix': row[3],
            'type': row[4],
            'quartier': row[5],
            'surface': row[6],
            'chambres': row[7],
            'date_publication': row[8],
            'source': row[9]
        })
    
    conn.close()
    return annonces

def get_all_annonces():
    """Récupère toutes les annonces"""
    conn = sqlite3.connect('annonces.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, titre, description, prix, type, quartier, surface, 
               chambres, date_publication, source
        FROM annonces 
        ORDER BY date_recuperation DESC
    ''')
    
    annonces = []
    for row in cursor.fetchall():
        annonces.append({
            'id': row[0],
            'titre': row[1],
            'description': row[2],
            'prix': row[3],
            'type': row[4],
            'quartier': row[5],
            'surface': row[6],
            'chambres': row[7],
            'date_publication': row[8],
            'source': row[9]
        })
    
    conn.close()
    return annonces

def get_statistiques():
    """Récupère les statistiques depuis la base de données"""
    conn = sqlite3.connect('annonces.db')
    cursor = conn.cursor()
    
    # Total annonces
    cursor.execute('SELECT COUNT(*) FROM annonces')
    total_annonces = cursor.fetchone()[0]
    
    # Annonces du jour
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('SELECT COUNT(*) FROM annonces WHERE date(date_publication) = date(?)', (today,))
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
    
    conn.close()
    
    return {
        'total_annonces': total_annonces,
        'annonces_aujourd_hui': annonces_aujourd_hui,
        'ventes': ventes,
        'locations': locations,
        'quartiers_actifs': quartiers_actifs
    }