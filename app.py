from flask import Flask, render_template, jsonify, request
import requests
from datetime import datetime, timedelta
import json
import os
from database import get_annonces_du_jour, get_all_annonces, get_statistiques, init_database

# Configuration pour Render
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'annonces.db')

# Initialiser la base de données au démarrage
init_database()

# Peupler la DB avec des données de test au démarrage si elle est vide
@app.before_first_request
def initialize_data():
    """Initialiser avec des données de test si la DB est vide"""
    try:
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM annonces')
        count = cursor.fetchone()[0]
        conn.close()
        
        if count == 0:
            print("🔄 Base de données vide, ajout de données de test...")
            from scraper import fetch_daily_ads
            fetch_daily_ads()
            print("✅ Données de test ajoutées")
    except Exception as e:
        print(f"❌ Erreur initialisation données: {e}")

@app.route('/')
def index():
    """Page d'accueil avec interface responsive"""
    return render_template('index.html')

@app.route('/api/annonces')
def get_annonces():
    """API pour récupérer toutes les annonces"""
    quartier = request.args.get('quartier', '').lower()
    type_annonce = request.args.get('type', '').lower()
    
    annonces = get_all_annonces()
    
    # Filtrer par quartier
    if quartier:
        annonces = [a for a in annonces if quartier in a['quartier'].lower()]
    
    # Filtrer par type
    if type_annonce:
        annonces = [a for a in annonces if type_annonce in a['type'].lower()]
    
    return jsonify({
        'annonces': annonces,
        'total': len(annonces),
        'date': datetime.now().isoformat()
    })

@app.route('/api/annonces/du-jour')
def get_annonces_du_jour_api():
    """API pour récupérer uniquement les annonces du jour"""
    quartier = request.args.get('quartier', '').lower()
    type_annonce = request.args.get('type', '').lower()
    
    annonces = get_annonces_du_jour()
    
    # Si pas d'annonces du jour, prendre toutes les annonces comme fallback
    if not annonces:
        print("🔄 Pas d'annonces du jour, récupération de toutes les annonces...")
        annonces = get_all_annonces()
    
    # Filtrer par quartier
    if quartier:
        annonces = [a for a in annonces if quartier in a['quartier'].lower()]
    
    # Filtrer par type
    if type_annonce:
        annonces = [a for a in annonces if type_annonce in a['type'].lower()]
    
    return jsonify({
        'annonces': annonces,
        'total': len(annonces),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'ville': 'Abidjan'
    })

@app.route('/api/annonces/<int:annonce_id>')
def get_annonce(annonce_id):
    """API pour récupérer une annonce spécifique"""
    # À implémenter : recherche dans la base de données
    return jsonify({'error': 'Fonction à implémenter'}), 404

@app.route('/api/quartiers')
def get_quartiers():
    """API pour récupérer la liste des quartiers"""
    # À implémenter : récupération depuis la base de données
    quartiers_abidjan = ['Plateau', 'Cocody', 'Treichville', 'Marcory', 'Yopougon', 
                        'Bingerville', 'Anyama', 'Koumassi', 'Port-Bouet', 'Rivera']
    return jsonify({
        'quartiers': quartiers_abidjan,
        'total': len(quartiers_abidjan)
    })

@app.route('/api/statistiques')
def get_statistiques_api():
    """API pour récupérer les statistiques"""
    try:
        stats = get_statistiques()
        return jsonify({'statistiques': stats})
    except Exception as e:
        print(f"Erreur récupération statistiques: {e}")
        return jsonify({'statistiques': {
            'total_annonces': 0,
            'annonces_aujourd_hui': 0,
            'ventes': 0,
            'locations': 0,
            'quartiers_actifs': 0
        }})

# Route health check pour Render
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Route pour forcer l'actualisation (pour tests)
@app.route('/admin/actualiser')
def force_refresh():
    """Route pour forcer l'actualisation des annonces"""
    try:
        # Importer et exécuter le scraper
        from scraper import fetch_daily_ads
        annonces = fetch_daily_ads()
        return jsonify({
            'status': 'success',
            'message': f'{len(annonces)} annonces récupérées',
            'date': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Route de debug pour voir le contenu de la DB
@app.route('/debug/db')
def debug_db():
    """Route de debug pour voir le contenu de la base de données"""
    try:
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM annonces')
        count = cursor.fetchone()[0]
        
        cursor.execute('SELECT * FROM annonces LIMIT 5')
        sample = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'total_annonces': count,
            'sample_annonces': [dict(row) for row in sample]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Configuration pour le développement local et Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)