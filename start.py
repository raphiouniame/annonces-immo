#!/usr/bin/env python3
"""
Script de démarrage pour initialiser l'application avec des données réalistes
"""

import os
import sys
import threading
import time
from datetime import datetime

# Ajouter le répertoire courant au PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))

def initialize_with_realistic_data():
    """Initialise la base de données avec des données réalistes"""
    print("🚀 Initialisation de l'application...")
    print("📞 Génération avec de vrais formats de numéros ivoiriens")
    
    try:
        from database import init_database
        # Utiliser le scraper amélioré au lieu du real_scraper
        from improved_scraper import fetch_daily_ads
        
        # Initialiser la base de données
        print("📊 Initialisation de la base de données...")
        init_database()
        
        # Générer des annonces réalistes avec vrais numéros
        print("📝 Génération d'annonces réalistes...")
        annonces = fetch_daily_ads()
        print(f"✅ {len(annonces)} annonces avec vrais numéros générées")
        
        # Afficher quelques exemples pour vérification
        print("\n📋 Exemples générés:")
        for i, annonce in enumerate(annonces[:3]):
            print(f"{i+1}. {annonce['titre']}")
            print(f"   Contact: {annonce['contact_nom']}")
            print(f"   Tél: {annonce['contact_telephone']}")
            print(f"   Prix: {annonce['prix']} FCFA")
            print()
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return False

def start_periodic_scraper():
    """Démarre le générateur périodique en arrière-plan"""
    def run_generator():
        while True:
            try:
                print("🔄 Exécution du générateur automatique...")
                from improved_scraper import fetch_daily_ads
                annonces = fetch_daily_ads()
                print(f"✅ Générateur terminé: {len(annonces)} annonces avec vrais numéros")
                
                # Attendre 6 heures avant la prochaine exécution (plus fréquent)
                time.sleep(6 * 60 * 60)
            except Exception as e:
                print(f"❌ Erreur générateur: {e}")
                # Attendre 30 minutes en cas d'erreur
                time.sleep(30 * 60)
    
    # Démarrer le générateur dans un thread séparé
    generator_thread = threading.Thread(target=run_generator, daemon=True)
    generator_thread.start()
    print("🤖 Générateur automatique démarré (toutes les 6h)")

if __name__ == "__main__":
    # Initialiser avec des données réalistes
    success = initialize_with_realistic_data()
    
    if not success:
        print("❌ Échec de l'initialisation, tentative avec le scraper de fallback...")
        try:
            from fake_scraper import fetch_daily_ads
            annonces = fetch_daily_ads()
            print(f"✅ Fallback réussi: {len(annonces)} annonces générées")
        except Exception as e:
            print(f"❌ Échec total: {e}")
    
    # Démarrer l'application Flask
    from app import app
    
    # Démarrer le générateur en arrière-plan
    start_periodic_scraper()
    
    # Lancer l'application
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Démarrage de l'application sur le port {port}")
    print(f"🔗 URL locale: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)