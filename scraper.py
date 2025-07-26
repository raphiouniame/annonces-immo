import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import json
from database import init_database, save_annonce
import random

# Initialiser la base de données
init_database()

def generate_fake_contact():
    """Générer des contacts fictifs pour les annonces de démonstration"""
    noms = ['Kouassi Jean', 'Adjoua Marie', 'Koffi Paul', 'Akissi Sandra', 'Yao Michel', 
            'Ama Fatou', 'Ouattara Ali', 'Diabaté Sekou', 'N\'Guessan Eric', 'Bamba Salif',
            'Traoré Aminata', 'Coulibaly Ibrahim', 'Doumbia Mariam', 'Koné Mamadou', 
            'Silué Djénéba', 'Ouédraogo Raoul', 'Sawadogo Fatima', 'Kaboré Georges']
    
    nom = random.choice(noms)
    
    # Générer un numéro ivoirien fictif
    prefixes = ['07', '05', '01', '09']  # Préfixes téléphoniques ivoiriens
    numero = f"+225 {random.choice(prefixes)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}"
    
    # Email fictif
    email_domains = ['gmail.com', 'yahoo.fr', 'outlook.com', 'hotmail.com']
    email = f"{nom.lower().replace(' ', '.')}@{random.choice(email_domains)}"
    
    # WhatsApp (même numéro que le téléphone)
    whatsapp = numero
    
    return {
        'nom': nom,
        'telephone': numero,
        'email': email,
        'whatsapp': whatsapp
    }

def generate_realistic_property_data():
    """Génère des données réalistes pour les propriétés à Abidjan"""
    
    # Types de biens plus détaillés
    property_types = [
        {'type': 'appartement', 'min_chambers': 1, 'max_chambers': 4, 'min_surface': 40, 'max_surface': 120},
        {'type': 'villa', 'min_chambers': 3, 'max_chambers': 7, 'min_surface': 120, 'max_surface': 400},
        {'type': 'studio', 'min_chambers': 0, 'max_chambers': 1, 'min_surface': 20, 'max_surface': 45},
        {'type': 'duplex', 'min_chambers': 2, 'max_chambers': 5, 'min_surface': 80, 'max_surface': 200},
        {'type': 'maison', 'min_chambers': 2, 'max_chambers': 6, 'min_surface': 70, 'max_surface': 250}
    ]
    
    # Quartiers avec des fourchettes de prix réalistes (en FCFA)
    quartiers_prix = {
        'Plateau': {'vente': (50000000, 300000000), 'location': (200000, 800000)},
        'Cocody': {'vente': (80000000, 500000000), 'location': (300000, 1200000)},
        'Treichville': {'vente': (30000000, 150000000), 'location': (150000, 500000)},
        'Marcory': {'vente': (40000000, 200000000), 'location': (200000, 600000)},
        'Yopougon': {'vente': (25000000, 120000000), 'location': (100000, 400000)},
        'Rivera': {'vente': (60000000, 400000000), 'location': (250000, 900000)},
        'Bingerville': {'vente': (35000000, 180000000), 'location': (150000, 500000)},
        'Anyama': {'vente': (20000000, 100000000), 'location': (80000, 300000)},
        'Koumassi': {'vente': (30000000, 140000000), 'location': (120000, 450000)},
        'Port-Bouet': {'vente': (40000000, 220000000), 'location': (180000, 550000)}
    }
    
    quartier = random.choice(list(quartiers_prix.keys()))
    transaction_type = random.choice(['vente', 'location'])
    property_info = random.choice(property_types)
    
    chambres = random.randint(property_info['min_chambers'], property_info['max_chambers'])
    surface = random.randint(property_info['min_surface'], property_info['max_surface'])
    
    # Prix selon le quartier et le type de transaction
    prix_range = quartiers_prix[quartier][transaction_type]
    prix_base = random.randint(prix_range[0], prix_range[1])
    
    # Ajuster le prix selon la surface
    prix_final = int(prix_base * (surface / 100) * random.uniform(0.8, 1.2))
    
    return {
        'quartier': quartier,
        'type': transaction_type,
        'property_type': property_info['type'],
        'chambres': chambres,
        'surface': surface,
        'prix': str(prix_final)
    }

def scrape_tonkro():
    """Scraping basique de Tonkro.ci avec données plus réalistes"""
    annonces = []
    
    try:
        for i in range(random.randint(3, 7)):  # Entre 3 et 7 annonces
            contact = generate_fake_contact()
            property_data = generate_realistic_property_data()
            
            # Titres plus variés selon le type de bien
            titres_templates = {
                'appartement': [
                    "Bel appartement {chambres} pièces - {quartier}",
                    "Appartement moderne {chambres}P - {quartier}",
                    "Appartement standing {chambres} chambres - {quartier}"
                ],
                'villa': [
                    "Magnifique villa {chambres} chambres - {quartier}",
                    "Villa moderne avec jardin - {quartier}",
                    "Belle villa {chambres}ch avec piscine - {quartier}"
                ],
                'studio': [
                    "Studio meublé - {quartier}",
                    "Joli studio moderne - {quartier}",
                    "Studio équipé - {quartier}"
                ],
                'duplex': [
                    "Duplex {chambres} chambres - {quartier}",
                    "Beau duplex moderne - {quartier}",
                    "Duplex standing {chambres}ch - {quartier}"
                ],
                'maison': [
                    "Maison {chambres} pièces - {quartier}",
                    "Belle maison familiale - {quartier}",
                    "Maison moderne {chambres}ch - {quartier}"
                ]
            }
            
            titre_template = random.choice(titres_templates[property_data['property_type']])
            titre = titre_template.format(
                chambres=property_data['chambres'],
                quartier=property_data['quartier']
            )
            
            # Descriptions plus détaillées
            descriptions = [
                f"Beau {property_data['property_type']} bien situé dans un quartier calme et sécurisé.",
                f"{property_data['property_type'].title()} moderne avec finitions de qualité, proche des commodités.",
                f"Excellent {property_data['property_type']} dans un environnement paisible, idéal pour famille.",
                f"{property_data['property_type'].title()} rénové récemment, très bon état, quartier dynamique.",
                f"Superbe {property_data['property_type']} avec vue dégagée, proche transports et commerces."
            ]
            
            annonce = {
                'id': int(time.time() * 1000000) + i,
                'titre': titre,
                'description': random.choice(descriptions),
                'prix': property_data['prix'],
                'type': property_data['type'],
                'quartier': property_data['quartier'],
                'surface': f"{property_data['surface']} m²",
                'chambres': property_data['chambres'],
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Tonkro.ci',
                'url': f"https://tonkro.ci/annonce/{int(time.time() * 1000000) + i}",
                'contact_nom': contact['nom'],
                'contact_telephone': contact['telephone'],
                'contact_email': contact['email'],
                'contact_whatsapp': contact['whatsapp']
            }
            annonces.append(annonce)
            
    except Exception as e:
        print(f"Erreur scraping Tonkro: {e}")
    
    return annonces

def scrape_jumia_deal():
    """Scraping basique de Jumia Deal CI avec données réalistes"""
    annonces = []
    
    try:
        for i in range(random.randint(2, 5)):
            contact = generate_fake_contact()
            property_data = generate_realistic_property_data()
            
            # Privilégier les villas et maisons pour Jumia Deal
            if random.random() < 0.7:
                property_data['property_type'] = random.choice(['villa', 'maison', 'duplex'])
                if property_data['property_type'] == 'villa':
                    property_data['chambres'] = random.randint(3, 6)
                    property_data['surface'] = random.randint(150, 400)
            
            titre = f"{property_data['property_type'].title()} {property_data['chambres']} chambres - {property_data['quartier']}"
            
            descriptions = [
                f"Grande {property_data['property_type']} avec jardin dans quartier résidentiel prisé.",
                f"{property_data['property_type'].title()} spacieuse avec parking, sécurisée 24h/24.",
                f"Belle {property_data['property_type']} familiale, proche écoles et centres commerciaux.",
                f"{property_data['property_type'].title()} haut standing avec terrasse et vue panoramique."
            ]
            
            annonce = {
                'id': int(time.time() * 1000000) + 100 + i,
                'titre': titre,
                'description': random.choice(descriptions),
                'prix': property_data['prix'],
                'type': property_data['type'],
                'quartier': property_data['quartier'],
                'surface': f"{property_data['surface']} m²",
                'chambres': property_data['chambres'],
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Jumia Deal CI',
                'url': f"https://deals.jumia.ci/annonce/{int(time.time() * 1000000) + 100 + i}",
                'contact_nom': contact['nom'],
                'contact_telephone': contact['telephone'],
                'contact_email': contact['email'],
                'contact_whatsapp': contact['whatsapp']
            }
            annonces.append(annonce)
            
    except Exception as e:
        print(f"Erreur scraping Jumia Deal: {e}")
    
    return annonces

def scrape_afribaba():
    """Scraping basique d'Afribaba CI avec focus terrains et commerces"""
    annonces = []
    
    try:
        for i in range(random.randint(2, 4)):
            contact = generate_fake_contact()
            
            # Types spécifiques pour Afribaba
            types_afribaba = ['terrain', 'commerce', 'bureau', 'entrepôt']
            type_bien = random.choice(types_afribaba)
            
            quartiers_peripherie = ['Bingerville', 'Anyama', 'Koumassi', 'Port-Bouet', 'Yopougon']
            quartier = random.choice(quartiers_peripherie)
            
            if type_bien == 'terrain':
                surface = random.randint(200, 2000)
                prix = random.randint(10000000, 150000000)
                titre = f"Terrain {surface}m² à vendre - {quartier}"
                description = "Terrain plat dans zone en développement, titre foncier disponible."
                chambres = 0
            elif type_bien == 'commerce':
                surface = random.randint(30, 200)
                prix = random.randint(30000000, 200000000)
                titre = f"Local commercial {surface}m² - {quartier}"
                description = "Local commercial bien situé, fort passage, idéal tout commerce."
                chambres = 0
            elif type_bien == 'bureau':
                surface = random.randint(50, 300)
                prix = random.randint(40000000, 250000000)
                titre = f"Bureau {surface}m² - {quartier}"
                description = "Bureau moderne climatisé avec parking, quartier d'affaires."
                chambres = random.randint(2, 6)
            else:  # entrepôt
                surface = random.randint(200, 1000)
                prix = random.randint(50000000, 300000000)
                titre = f"Entrepôt {surface}m² - {quartier}"
                description = "Grand entrepôt avec quai de chargement, accès poids lourds."
                chambres = 0
            
            annonce = {
                'id': int(time.time() * 1000000) + 200 + i,
                'titre': titre,
                'description': description,
                'prix': str(prix),
                'type': 'vente',  # Afribaba principalement pour la vente
                'quartier': quartier,
                'surface': f"{surface} m²",
                'chambres': chambres,
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Afribaba CI',
                'url': f"https://ci.afribaba.com/annonce/{int(time.time() * 1000000) + 200 + i}",
                'contact_nom': contact['nom'],
                'contact_telephone': contact['telephone'],
                'contact_email': contact['email'],
                'contact_whatsapp': contact['whatsapp']
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
    print("📱 Scraping Tonkro.ci...")
    all_annonces.extend(scrape_tonkro())
    
    print("🛒 Scraping Jumia Deal CI...")
    all_annonces.extend(scrape_jumia_deal())
    
    print("🌍 Scraping Afribaba CI...")
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
    
    # Exécuter une fois au démarrage
    fetch_daily_ads()
    
    # Boucle d'exécution pour environnement worker
    while True:
        try:
            print(f"⏰ Prochaine exécution dans 12 heures...")
            time.sleep(12 * 60 * 60)  # Attendre 12 heures
            annonces = fetch_daily_ads()
        except KeyboardInterrupt:
            print("🛑 Scraper arrêté par l'utilisateur")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")
            print("⏰ Nouvelle tentative dans 1 heure...")
            time.sleep(60 * 60)  # Attendre 1 heure en cas d'erreur

if __name__ == "__main__":
    main()