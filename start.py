#!/usr/bin/env python3
"""
Script de démarrage pour initialiser l'application avec des données
"""

import os
import sys
import threading
import time
from datetime import datetime

# Ajouter le répertoire courant au PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))

def initialize_with_sample_data():
    """Initialise la base de données avec des données d'exemple"""
    print("🚀 Initialisation de l'application...")
    
    try:
        from database import init_database
        from real_scraper import fetch_daily_ads
        
        # Initialiser la base de données
        print("📊 Initialisation de la base de données...")
        init_database()
        
        # Générer des annonces d'exemple
        print("📝 Génération d'annonces d'exemple...")
        annonces = fetch_daily_ads()
        print(f"✅ {len(annonces)} annonces générées")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return False

def start_periodic_scraper():
    """Démarre le scraper périodique en arrière-plan"""
    def run_scraper():
        while True:
            try:
                print("🔄 Exécution du scraper automatique...")
                from real_scraper import fetch_daily_ads
                annonces = fetch_daily_ads()
                print(f"✅ Scraper terminé: {len(annonces)} annonces")
                
                # Attendre 12 heures avant la prochaine exécution
                time.sleep(12 * 60 * 60)
            except Exception as e:
                print(f"❌ Erreur scraper: {e}")
                # Attendre 1 heure en cas d'erreur
                time.sleep(60 * 60)
    
    # Démarrer le scraper dans un thread séparé
    scraper_thread = threading.Thread(target=run_scraper, daemon=True)
    scraper_thread.start()
    print("🤖 Scraper automatique démarré")

if __name__ == "__main__":
    # Initialiser avec des données d'exemple
    initialize_with_sample_data()
    
    # Démarrer l'application Flask
    from app import app
    
    # Démarrer le scraper en arrière-plan
    start_periodic_scraper()
    
    # Lancer l'application
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Démarrage de l'application sur le port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)