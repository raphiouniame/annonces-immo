from flask import Flask, render_template, jsonify, request
import requests
from datetime import datetime, timedelta
import json
import os

# Configuration pour Render
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')

# Pour Render - utiliser le port fourni par l'environnement
port = int(os.environ.get('PORT', 5000))

# Données de démonstration
DEMO_ANNONCES = [
    {
        "id": 1,
        "titre": "Appartement 3 pièces - Cocody",
        "description": "Bel appartement meublé dans un quartier calme",
        "prix": "120000000",
        "type": "vente",
        "quartier": "Cocody",
        "surface": "85 m²",
        "chambres": 2,
        "date_publication": "2024-01-15",
        "image": "https://via.placeholder.com/300x200/4CAF50/white?text=Appartement"
    },
    {
        "id": 2,
        "titre": "Studio à louer - Plateau",
        "description": "Studio moderne avec climatisation",
        "prix": "150000",
        "type": "location",
        "quartier": "Plateau",
        "surface": "35 m²",
        "chambres": 1,
        "date_publication": "2024-01-15",
        "image": "https://via.placeholder.com/300x200/2196F3/white?text=Studio"
    },
    {
        "id": 3,
        "titre": "Villa 4 chambres - Marcory",
        "description": "Grande villa avec jardin et piscine",
        "prix": "250000000",
        "type": "vente",
        "quartier": "Marcory",
        "surface": "200 m²",
        "chambres": 4,
        "date_publication": "2024-01-14",
        "image": "https://via.placeholder.com/300x200/FF9800/white?text=Villa"
    },
    {
        "id": 4,
        "titre": "Terrain à Bingerville",
        "description": "Terrain plat de 500 m² près de la lagune",
        "prix": "80000000",
        "type": "vente",
        "quartier": "Bingerville",
        "surface": "500 m²",
        "chambres": 0,
        "date_publication": "2024-01-15",
        "image": "https://via.placeholder.com/300x200/9C27B0/white?text=Terrain"
    },
    {
        "id": 5,
        "titre": "Duplex à louer - Yopougon",
        "description": "Duplex spacieux dans un quartier résidentiel",
        "prix": "200000",
        "type": "location",
        "quartier": "Yopougon",
        "surface": "120 m²",
        "chambres": 3,
        "date_publication": "2024-01-15",
        "image": "https://via.placeholder.com/300x200/E91E63/white?text=Duplex"
    },
    {
        "id": 6,
        "titre": "Appartement neuf - Rivera",
        "description": "Appartement neuf avec vue sur lagune",
        "prix": "180000000",
        "type": "vente",
        "quartier": "Rivera",
        "surface": "100 m²",
        "chambres": 3,
        "date_publication": "2024-01-15",
        "image": "https://via.placeholder.com/300x200/00BCD4/white?text=Neuf"
    }
]

@app.route('/')
def index():
    """Page d'accueil avec interface responsive"""
    return render_template('index.html')

@app.route('/api/annonces')
def get_annonces():
    """API pour récupérer toutes les annonces"""
    quartier = request.args.get('quartier', '').lower()
    type_annonce = request.args.get('type', '').lower()
    date = request.args.get('date', '')
    
    annonces = DEMO_ANNONCES
    
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
def get_annonces_du_jour():
    """API pour récupérer uniquement les annonces du jour"""
    quartier = request.args.get('quartier', '').lower()
    type_annonce = request.args.get('type', '').lower()
    
    today = datetime.now().strftime('%Y-%m-%d')
    annonces = [a for a in DEMO_ANNONCES if a['date_publication'] == today]
    
    # Filtrer par quartier
    if quartier:
        annonces = [a for a in annonces if quartier in a['quartier'].lower()]
    
    # Filtrer par type
    if type_annonce:
        annonces = [a for a in annonces if type_annonce in a['type'].lower()]
    
    return jsonify({
        'annonces': annonces,
        'total': len(annonces),
        'date': today,
        'ville': 'Abidjan'
    })

@app.route('/api/annonces/<int:annonce_id>')
def get_annonce(annonce_id):
    """API pour récupérer une annonce spécifique"""
    annonce = next((a for a in DEMO_ANNONCES if a['id'] == annonce_id), None)
    if annonce:
        return jsonify(annonce)
    return jsonify({'error': 'Annonce non trouvée'}), 404

@app.route('/api/quartiers')
def get_quartiers():
    """API pour récupérer la liste des quartiers"""
    quartiers = list(set([a['quartier'] for a in DEMO_ANNONCES]))
    return jsonify({
        'quartiers': sorted(quartiers),
        'total': len(quartiers)
    })

@app.route('/api/statistiques')
def get_statistiques():
    """API pour récupérer les statistiques"""
    total_annonces = len(DEMO_ANNONCES)
    today = datetime.now().strftime('%Y-%m-%d')
    annonces_aujourd_hui = len([a for a in DEMO_ANNONCES if a['date_publication'] == today])
    ventes = len([a for a in DEMO_ANNONCES if a['type'] == 'vente'])
    locations = len([a for a in DEMO_ANNONCES if a['type'] == 'location'])
    
    return jsonify({
        'statistiques': {
            'total_annonces': total_annonces,
            'annonces_aujourd_hui': annonces_aujourd_hui,
            'ventes': ventes,
            'locations': locations,
            'quartiers_actifs': len(set([a['quartier'] for a in DEMO_ANNONCES]))
        }
    })

# Route health check pour Render
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Configuration pour Render
    app.run(host='0.0.0.0', port=port, debug=False)