import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import json
from database import init_database, save_annonce
import random

# Initialiser la base de données
init_database()

def scrape_tonkro():
    """Scraping basique de Tonkro.ci (à adapter selon le site réel)"""
    annonces = []
    
    try:
        # Exemple d'URL de recherche (à adapter)
        url = "https://tonkro.ci/search?category=immobilier&location=abidjan"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Exemple de parsing (à adapter selon la structure réelle du site)
        # annonces_elements = soup.find_all('div', class_='annonce-item')
        
        # Pour l'exemple, créons quelques annonces fictives
        quartiers_abidjan = ['Plateau', 'Cocody', 'Treichville', 'Marcory', 'Yopougon']
        types = ['vente', 'location']
        
        for i in range(3):  # 3 annonces par exécution
            annonce = {
                'id': int(time.time() * 1000000) + i,  # ID unique
                'titre': f"Appartement {random.randint(2,4)} pièces - {random.choice(quartiers_abidjan)}",
                'description': "Bel appartement bien situé dans un quartier calme",
                'prix': str(random.randint(50000, 500000000)),  # En FCFA
                'type': random.choice(types),
                'quartier': random.choice(quartiers_abidjan),
                'surface': f"{random.randint(50, 200)} m²",
                'chambres': random.randint(1, 5),
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Tonkro.ci',
                'url': f"https://tonkro.ci/annonce/{int(time.time() * 1000000) + i}"
            }
            annonces.append(annonce)
            
    except Exception as e:
        print(f"Erreur scraping Tonkro: {e}")
    
    return annonces

def scrape_jumia_deal():
    """Scraping basique de Jumia Deal CI"""
    annonces = []
    
    try:
        # Exemple d'URL (à adapter)
        url = "https://deals.jumia.ci/immobilier-abidjan"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        # Parsing à implémenter selon la structure réelle
        
        # Pour l'exemple, créons quelques annonces
        quartiers_abidjan = ['Plateau', 'Cocody', 'Treichville', 'Marcory', 'Rivera']
        types = ['vente', 'location']
        
        for i in range(2):
            annonce = {
                'id': int(time.time() * 1000000) + 100 + i,
                'titre': f"Villa {random.randint(3,6)} chambres - {random.choice(quartiers_abidjan)}",
                'description': "Grande villa avec jardin dans quartier résidentiel",
                'prix': str(random.randint(100000000, 800000000)),  # En FCFA
                'type': random.choice(types),
                'quartier': random.choice(quartiers_abidjan),
                'surface': f"{random.randint(150, 500)} m²",
                'chambres': random.randint(3, 6),
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Jumia Deal CI',
                'url': f"https://deals.jumia.ci/annonce/{int(time.time() * 1000000) + 100 + i}"
            }
            annonces.append(annonce)
            
    except Exception as e:
        print(f"Erreur scraping Jumia Deal: {e}")
    
    return annonces

def scrape_afribaba():
    """Scraping basique d'Afribaba CI"""
    annonces = []
    
    try:
        # Pour l'exemple, créons quelques annonces
        quartiers_abidjan = ['Bingerville', 'Anyama', 'Koumassi', 'Port-Bouet']
        types = ['vente', 'location']
        
        for i in range(2):
            annonce = {
                'id': int(time.time() * 1000000) + 200 + i,
                'titre': f"Terrain à vendre - {random.choice(quartiers_abidjan)}",
                'description': "Terrain plat dans zone en développement",
                'prix': str(random.randint(20000000, 200000000)),  # En FCFA
                'type': 'vente',
                'quartier': random.choice(quartiers_abidjan),
                'surface': f"{random.randint(200, 1000)} m²",
                'chambres': 0,
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Afribaba CI',
                'url': f"https://ci.afribaba.com/annonce/{int(time.time() * 1000000) + 200 + i}"
            }
            annonces.append(annonce)
            
    except Exception as e:
        print(f"Erreur scraping Afribaba: {e}")
    
    return annonces

def fetch_daily_ads():
    """Fonction principale pour récupérer les annonces du jour"""
    print(f"🔄 Récupération des annonces du {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_annonces = []
    
    # Récupérer les annonces de différentes sources
    all_annonces.extend(scrape_tonkro())
    all_annonces.extend(scrape_jumia_deal())
    all_annonces.extend(scrape_afribaba())
    
    # Sauvegarder les annonces
    saved_count = 0
    for annonce in all_annonces:
        if save_annonce(annonce):
            saved_count += 1
    
    print(f"✅ {saved_count}/{len(all_annonces)} annonces sauvegardées")
    return all_annonces

def main():
    """Fonction principale du scraper"""
    print("🚀 Démarrage du scraper d'annonces immobilières d'Abidjan")
    
    # Boucle d'exécution
    while True:
        try:
            annonces = fetch_daily_ads()
            print(f"⏰ Prochaine exécution dans 24 heures...")
            time.sleep(24 * 60 * 60)  # Attendre 24 heures
        except KeyboardInterrupt:
            print("🛑 Scraper arrêté par l'utilisateur")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")
            print("⏰ Nouvelle tentative dans 1 heure...")
            time.sleep(60 * 60)  # Attendre 1 heure en cas d'erreur

if __name__ == "__main__":
    main()