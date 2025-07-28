from flask import Flask, render_template, jsonify, request
import requests
from datetime import datetime, timedelta
import json
import os
from database import get_annonces_du_jour, get_all_annonces, get_statistiques, init_database
import threading

# Configuration pour Render
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'annonces.db')

# Variable pour s'assurer que l'initialisation ne se fait qu'une fois
_initialized = False
_init_lock = threading.Lock()

def ensure_database_initialized():
    """Initialise la base de données de manière thread-safe"""
    global _initialized
    if not _initialized:
        with _init_lock:
            if not _initialized:
                success = init_database()
                if success:
                    _initialized = True
                    print("✅ Base de données initialisée avec succès")
                else:
                    print("❌ Échec de l'initialisation de la base de données")

def generate_test_annonces():
    """Génère des annonces de test si aucune donnée n'est disponible"""
    return [
        {
            'id': 1,
            'titre': 'Appartement 3P moderne - Cocody',
            'description': 'Bel appartement bien situé dans un quartier calme et sécurisé. Proche des commodités.',
            'prix': '120000000',
            'type': 'vente',
            'quartier': 'Cocody',
            'surface': '85 m²',
            'chambres': 2,
            'date_publication': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Tonkro.ci',
            'url': 'https://tonkro.ci/annonce/1',
            'contact_nom': 'Kouassi Jean',
            'contact_telephone': '+225 07 12 34 56 78',
            'contact_email': 'kouassi.jean@gmail.com',
            'contact_whatsapp': '22507123456',
            'image': 'https://via.placeholder.com/300x200?text=Appartement'
        },
        {
            'id': 2,
            'titre': 'Villa 4ch avec jardin - Plateau',
            'description': 'Magnifique villa moderne avec finitions de qualité, carrelage au sol, cuisine aménagée.',
            'prix': '250000000',
            'type': 'vente',
            'quartier': 'Plateau',
            'surface': '180 m²',
            'chambres': 4,
            'date_publication': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Jumia Deal CI',
            'url': 'https://deals.jumia.ci/annonce/2',
            'contact_nom': 'Adjoua Marie',
            'contact_telephone': '+225 05 98 76 54 32',
            'contact_email': 'adjoua.marie@yahoo.fr',
            'contact_whatsapp': '22505987654',
            'image': 'https://via.placeholder.com/300x200?text=Villa'
        },
        {
            'id': 3,
            'titre': 'Studio meublé - Treichville',
            'description': 'Joli studio climatisé tout confort, proche centres commerciaux et arrêts de transport.',
            'prix': '150000',
            'type': 'location',
            'quartier': 'Treichville',
            'surface': '35 m²',
            'chambres': 0,
            'date_publication': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Expat Abidjan',
            'url': 'https://expat-abidjan.com/annonce/3',
            'contact_nom': 'Koffi Paul',
            'contact_telephone': '+225 01 45 67 89 01',
            'contact_email': 'koffi.paul@outlook.com',
            'contact_whatsapp': '22501456789',
            'image': 'https://via.placeholder.com/300x200?text=Studio'
        },
        {
            'id': 4,
            'titre': 'Duplex 3ch standing - Rivera',
            'description': 'Duplex moderne avec terrasse et vue. Résidence sécurisée avec piscine commune.',
            'prix': '180000000',
            'type': 'vente',
            'quartier': 'Rivera',
            'surface': '140 m²',
            'chambres': 3,
            'date_publication': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Tonkro.ci',
            'url': 'https://tonkro.ci/annonce/4',
            'contact_nom': 'Traoré Aminata',
            'contact_telephone': '+225 67 33 44 55 66',
            'contact_email': 'traore.aminata@gmail.com',
            'contact_whatsapp': '22567334455',
            'image': 'https://via.placeholder.com/300x200?text=Duplex'
        }
    ]

@app.route('/')
def index():
    """Page d'accueil avec interface responsive"""
    ensure_database_initialized()
    return render_template('index.html')

@app.route('/api/annonces')
def get_annonces():
    """API pour récupérer toutes les annonces"""
    ensure_database_initialized()
    quartier = request.args.get('quartier', '').lower()
    type_annonce = request.args.get('type', '').lower()
    
    try:
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
    except Exception as e:
        print(f"Erreur récupération annonces: {e}")
        return jsonify({
            'annonces': [],
            'total': 0,
            'date': datetime.now().isoformat(),
            'error': str(e)
        })

@app.route('/api/annonces/du-jour')
def get_annonces_du_jour_api():
    """API pour récupérer uniquement les annonces du jour"""
    ensure_database_initialized()
    quartier = request.args.get('quartier', '').lower()
    type_annonce = request.args.get('type', '').lower()
    
    try:
        annonces = get_annonces_du_jour()
        # Si pas d'annonces du jour, essayer de générer
        if len(annonces) == 0:
            print("⚠️ Aucune annonce du jour trouvée, tentative de génération...")
            try:
                from improved_scraper import fetch_daily_ads
                nouvelles_annonces = fetch_daily_ads()
                print(f"✅ {len(nouvelles_annonces)} nouvelles annonces générées")
                # Récupérer à nouveau
                annonces = get_annonces_du_jour()
            except Exception as gen_error:
                print(f"❌ Erreur génération annonces: {gen_error}")
                # Retourner des annonces de test
                annonces = generate_test_annonces()
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
    except Exception as e:
        print(f"Erreur récupération annonces du jour: {e}")
        return jsonify({
            'annonces': generate_test_annonces(),
            'total': 4,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'ville': 'Abidjan',
            'error': str(e)
        })

@app.route('/api/annonces/<int:annonce_id>')
def get_annonce(annonce_id):
    """API pour récupérer une annonce spécifique"""
    # À implémenter : recherche dans la base de données
    return jsonify({'error': 'Fonction à implémenter'}), 404

@app.route('/api/quartiers')
def get_quartiers():
    """API pour récupérer la liste des quartiers"""
    quartiers_abidjan = ['Plateau', 'Cocody', 'Treichville', 'Marcory', 'Yopougon', 
                        'Bingerville', 'Anyama', 'Koumassi', 'Port-Bouet', 'Rivera']
    return jsonify({
        'quartiers': quartiers_abidjan,
        'total': len(quartiers_abidjan)
    })

@app.route('/api/statistiques')
def get_statistiques_api():
    """API pour récupérer les statistiques"""
    ensure_database_initialized()
    try:
        stats = get_statistiques()
        # Si pas de statistiques, en générer de base
        if stats['total_annonces'] == 0:
            stats = {
                'total_annonces': 4,
                'annonces_aujourd_hui': 4,
                'ventes': 3,
                'locations': 1,
                'quartiers_actifs': 4
            }
        return jsonify({'statistiques': stats})
    except Exception as e:
        print(f"Erreur récupération statistiques: {e}")
        return jsonify({'statistiques': {
            'total_annonces': 4,
            'annonces_aujourd_hui': 4,
            'ventes': 3,
            'locations': 1,
            'quartiers_actifs': 4
        }})

# Route health check pour Render
@app.route('/health')
def health_check():
    ensure_database_initialized()
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'database': 'initialized' if _initialized else 'not_initialized'
    })

# Route pour forcer l'actualisation (pour tests)
@app.route('/admin/actualiser')
def force_refresh():
    """Route pour forcer l'actualisation des annonces"""
    ensure_database_initialized()
    try:
        from improved_scraper import fetch_daily_ads
        annonces = fetch_daily_ads()
        return jsonify({
            'status': 'success',
            'message': f'{len(annonces)} annonces réalistes récupérées',
            'date': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Configuration pour le développement local et Render
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)