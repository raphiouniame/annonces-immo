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
    print("🌟 Initialisation de l'application Annonces Immobilières Abidjan")
    print("📞 Génération avec de vrais formats de numéros ivoiriens")
    try:
        from database import init_database
        # Utiliser le scraper amélioré
        from improved_scraper import fetch_daily_ads
        
        # Initialiser la base de données
        print("📊 Initialisation de la base de données...")
        success = init_database()
        if not success:
            print("❌ Échec initialisation base de données")
            return False
            
        # Générer des annonces réalistes
        print("📝 Génération d'annonces réalistes...")
        annonces = fetch_daily_ads()
        print(f"✅ {len(annonces)} annonces avec vrais numéros générées")
        
        if len(annonces) > 0:
            # Afficher quelques exemples pour vérification
            print("\n📋 Exemples générés:")
            for i, annonce in enumerate(annonces[:3]):
                print(f"{i+1}. {annonce['titre']}")
                print(f"   Contact: {annonce['contact_nom']}")
                print(f"   Tél: {annonce['contact_telephone']}")
                print(f"   Prix: {annonce['prix']} FCFA")
                print()
            return True
        else:
            print("⚠️ Aucune annonce générée, génération manuelle...")
            return generate_manual_test_data()
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        print("🔧 Tentative de génération manuelle...")
        return generate_manual_test_data()

def generate_manual_test_data():
    """Génère manuellement quelques annonces de test si le scraper échoue"""
    try:
        from database import save_annonce
        test_annonces = [
            {
                'id': int(time.time() * 1000000),
                'titre': 'Appartement 3 pièces moderne - Cocody',
                'description': 'Bel appartement bien situé dans un quartier calme et sécurisé. Proche des commodités (écoles, marchés, transports). Idéal pour famille.',
                'prix': '120000000',
                'type': 'vente',
                'quartier': 'Cocody',
                'surface': '85 m²',
                'chambres': 2,
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Tonkro.ci',
                'url': f"https://tonkro.ci/annonce/{int(time.time() * 1000000)}",
                'contact_nom': 'Kouassi Jean',
                'contact_telephone': '+225 07 12 34 56 78',
                'contact_email': 'kouassi.jean@gmail.com',
                'contact_whatsapp': '22507123456'
            },
            {
                'id': int(time.time() * 1000000) + 1,
                'titre': 'Villa 4 chambres avec jardin - Plateau',
                'description': 'Magnifique villa moderne avec finitions de qualité, carrelage au sol, cuisine aménagée. Quartier dynamique avec bon voisinage.',
                'prix': '250000000',
                'type': 'vente',
                'quartier': 'Plateau',
                'surface': '180 m²',
                'chambres': 4,
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Jumia Deal CI',
                'url': f"https://deals.jumia.ci/annonce/{int(time.time() * 1000000) + 1}",
                'contact_nom': 'Adjoua Marie',
                'contact_telephone': '+225 05 98 76 54 32',
                'contact_email': 'adjoua.marie@yahoo.fr',
                'contact_whatsapp': '22505987654'
            },
            {
                'id': int(time.time() * 1000000) + 2,
                'titre': 'Studio meublé moderne - Treichville',
                'description': 'Joli studio climatisé tout confort, proche centres commerciaux et arrêts de transport. Parfait pour jeunes professionnels.',
                'prix': '150000',
                'type': 'location',
                'quartier': 'Treichville',
                'surface': '35 m²',
                'chambres': 0,
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Expat Abidjan',
                'url': f"https://expat-abidjan.com/annonce/{int(time.time() * 1000000) + 2}",
                'contact_nom': 'Koffi Paul',
                'contact_telephone': '+225 01 45 67 89 01',
                'contact_email': 'koffi.paul@outlook.com',
                'contact_whatsapp': '22501456789'
            },
            {
                'id': int(time.time() * 1000000) + 3,
                'titre': 'Duplex 3 chambres standing - Rivera',
                'description': 'Duplex moderne avec terrasse et vue dégagée. Résidence sécurisée avec piscine commune et salle de sport.',
                'prix': '180000000',
                'type': 'vente',
                'quartier': 'Rivera',
                'surface': '140 m²',
                'chambres': 3,
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Tonkro.ci',
                'url': f"https://tonkro.ci/annonce/{int(time.time() * 1000000) + 3}",
                'contact_nom': 'Traoré Aminata',
                'contact_telephone': '+225 67 33 44 55 66',
                'contact_email': 'traore.aminata@gmail.com',
                'contact_whatsapp': '22567334455'
            }
        ]
        saved_count = 0
        for annonce in test_annonces:
            if save_annonce(annonce):
                saved_count += 1
        print(f"✅ {saved_count} annonces de test générées manuellement")
        return saved_count > 0
    except Exception as e:
        print(f"❌ Erreur génération manuelle: {e}")
        return False

def start_periodic_scraper():
    """Démarre le générateur périodique en arrière-plan"""
    def run_generator():
        # Attendre 1 minute avant la première exécution
        time.sleep(60)
        while True:
            try:
                print("🔄 Exécution du générateur automatique...")
                from improved_scraper import fetch_daily_ads
                annonces = fetch_daily_ads()
                print(f"✅ Générateur terminé: {len(annonces)} annonces avec vrais numéros")
                # Attendre 6 heures avant la prochaine exécution
                time.sleep(6 * 60 * 60)
            except Exception as e:
                print(f"❌ Erreur générateur: {e}")
                # Attendre 1 heure en cas d'erreur
                time.sleep(60 * 60)
                
    # Démarrer le générateur dans un thread séparé
    generator_thread = threading.Thread(target=run_generator, daemon=True)
    generator_thread.start()
    print("🤖 Générateur automatique démarré (première exec dans 1min, puis toutes les 6h)")

if __name__ == "__main__":
    # Initialiser avec des données réalistes
    success = initialize_with_realistic_data()
    if not success:
        print("❌ Échec total de l'initialisation des données")
        print("⚠️ L'application va démarrer sans données initiales")
    
    # Démarrer l'application Flask
    print("📱 Import de l'application Flask...")
    from app import app
    
    # Démarrer le générateur en arrière-plan
    start_periodic_scraper()
    
    # Lancer l'application
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Démarrage de l'application sur le port {port}")
    print(f"🔗 Application prête !")
    
    # Pour le développement local
    if os.environ.get('FLASK_ENV') == 'development':
        print(f"🔗 URL locale: http://localhost:{port}")
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        # Pour la production (Render) - Laisser Gunicorn gérer l'application
        # On garde le processus en vie sans démarrer Flask directement
        print("✅ Initialisation terminée. En attente de requêtes via Gunicorn...")
        try:
            # Garder le thread principal actif
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n Arrêt de l'application.")