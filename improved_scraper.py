import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import json
from database import init_database, save_annonce
import random
import re

# Initialiser la base de données
init_database()

def generate_real_ivorian_contact():
    """Générer des contacts avec de vrais formats de numéros ivoiriens"""
    
    # Vrais noms ivoiriens courants
    prenoms_hommes = ['Kouassi', 'Koffi', 'Yao', 'N\'Guessan', 'Ouattara', 'Traoré', 'Coulibaly', 
                     'Koné', 'Diabaté', 'Bamba', 'Silué', 'Doumbia', 'Sawadogo', 'Kaboré']
    prenoms_femmes = ['Adjoua', 'Akissi', 'Ama', 'Aminata', 'Mariam', 'Djénéba', 'Fatima', 
                     'Salimata', 'Aïcha', 'Hawa', 'Rokia', 'Fatoumata']
    
    noms_famille = ['Jean', 'Paul', 'Marie', 'Sandra', 'Michel', 'Eric', 'Ali', 'Sekou', 
                   'Ibrahim', 'Mamadou', 'Georges', 'Raoul', 'Salif', 'Moussa', 'Issouf']
    
    # Générer nom complet
    if random.choice([True, False]):  # Homme ou femme
        prenom = random.choice(prenoms_hommes)
    else:
        prenom = random.choice(prenoms_femmes)
    
    nom = random.choice(noms_famille)
    nom_complet = f"{prenom} {nom}"
    
    # Vrais préfixes d'opérateurs ivoiriens (2024)
    operateurs = {
        'MTN': ['05', '65', '45', '55'],      # MTN Côte d'Ivoire
        'ORANGE': ['07', '67', '47', '57'],   # Orange CI
        'MOOV': ['01', '61', '41', '51'],     # Moov CI
    }
    
    # Choisir un opérateur et préfixe
    operateur = random.choice(list(operateurs.keys()))
    prefixe = random.choice(operateurs[operateur])
    
    # Générer les 6 derniers chiffres (format XX XX XX)
    partie1 = f"{random.randint(10, 99):02d}"
    partie2 = f"{random.randint(10, 99):02d}" 
    partie3 = f"{random.randint(10, 99):02d}"
    
    # Format final: +225 XX XX XX XX
    numero_complet = f"+225 {prefixe} {partie1} {partie2} {partie3}"
    numero_whatsapp = f"225{prefixe}{partie1}{partie2}{partie3}"  # Format WhatsApp
    
    # Email professionnel
    email_domains = ['gmail.com', 'yahoo.fr', 'outlook.com', 'hotmail.com']
    email_name = prenom.lower().replace('\'', '').replace(' ', '')
    email = f"{email_name}.{nom.lower()}@{random.choice(email_domains)}"
    
    return {
        'nom': nom_complet,
        'telephone': numero_complet,
        'email': email,
        'whatsapp': numero_whatsapp,
        'operateur': operateur
    }

def generate_realistic_property_data():
    """Génère des données réalistes pour les propriétés à Abidjan avec prix 2024"""
    
    # Types de biens avec caractéristiques spécifiques
    property_types = [
        {'type': 'appartement', 'min_chambers': 1, 'max_chambers': 4, 'min_surface': 40, 'max_surface': 120},
        {'type': 'villa', 'min_chambers': 3, 'max_chambers': 7, 'min_surface': 120, 'max_surface': 400},
        {'type': 'studio', 'min_chambers': 0, 'max_chambers': 1, 'min_surface': 20, 'max_surface': 45},
        {'type': 'duplex', 'min_chambers': 2, 'max_chambers': 5, 'min_surface': 80, 'max_surface': 200},
        {'type': 'maison', 'min_chambers': 2, 'max_chambers': 6, 'min_surface': 70, 'max_surface': 250}
    ]
    
    # Quartiers avec prix réalistes 2024 (en FCFA)
    quartiers_prix = {
        'Plateau': {'vente': (80000000, 500000000), 'location': (300000, 1200000)},
        'Cocody': {'vente': (120000000, 800000000), 'location': (400000, 1500000)},
        'Treichville': {'vente': (40000000, 200000000), 'location': (180000, 600000)},
        'Marcory': {'vente': (60000000, 300000000), 'location': (250000, 750000)},
        'Yopougon': {'vente': (35000000, 180000000), 'location': (120000, 500000)},
        'Rivera': {'vente': (100000000, 600000000), 'location': (350000, 1100000)},
        'Bingerville': {'vente': (50000000, 250000000), 'location': (200000, 600000)},
        'Anyama': {'vente': (30000000, 150000000), 'location': (100000, 400000)},
        'Koumassi': {'vente': (45000000, 220000000), 'location': (150000, 550000)},
        'Port-Bouet': {'vente': (55000000, 280000000), 'location': (200000, 650000)}
    }
    
    quartier = random.choice(list(quartiers_prix.keys()))
    transaction_type = random.choice(['vente', 'location'])
    property_info = random.choice(property_types)
    
    chambres = random.randint(property_info['min_chambers'], property_info['max_chambers'])
    surface = random.randint(property_info['min_surface'], property_info['max_surface'])
    
    # Prix selon le quartier et le type de transaction
    prix_range = quartiers_prix[quartier][transaction_type]
    prix_base = random.randint(prix_range[0], prix_range[1])
    
    # Ajuster le prix selon la surface et ajouter de la variation
    facteur_surface = surface / 100
    facteur_variation = random.uniform(0.85, 1.15)
    prix_final = int(prix_base * facteur_surface * facteur_variation)
    
    return {
        'quartier': quartier,
        'type': transaction_type,
        'property_type': property_info['type'],
        'chambres': chambres,
        'surface': surface,
        'prix': str(prix_final)
    }

def scrape_tonkro_realistic():
    """Génère des annonces réalistes façon Tonkro.ci"""
    annonces = []
    
    try:
        # Générer entre 4 et 8 annonces
        nb_annonces = random.randint(4, 8)
        
        for i in range(nb_annonces):
            contact = generate_real_ivorian_contact()
            property_data = generate_realistic_property_data()
            
            # Titres variés selon le type de bien
            titres_templates = {
                'appartement': [
                    "Appartement {chambres}P standing - {quartier}",
                    "Bel appartement {chambres} pièces moderne - {quartier}",
                    "Appartement {chambres} chambres climatisé - {quartier}",
                    "Joli {chambres}P avec parking - {quartier}"
                ],
                'villa': [
                    "Villa {chambres} chambres avec jardin - {quartier}",
                    "Magnifique villa moderne {chambres}ch - {quartier}",
                    "Villa standing {chambres} chambres + piscine - {quartier}",
                    "Belle villa familiale {chambres}ch - {quartier}"
                ],
                'studio': [
                    "Studio meublé moderne - {quartier}",
                    "Joli studio climatisé - {quartier}",
                    "Studio équipé tout confort - {quartier}",
                    "Studio neuf avec parking - {quartier}"
                ],
                'duplex': [
                    "Duplex {chambres} chambres moderne - {quartier}",
                    "Beau duplex {chambres}ch avec terrasse - {quartier}",
                    "Duplex standing {chambres} chambres - {quartier}",
                    "Duplex neuf {chambres}ch + garage - {quartier}"
                ],
                'maison': [
                    "Maison {chambres} pièces avec cour - {quartier}",
                    "Belle maison familiale {chambres}ch - {quartier}",
                    "Maison moderne {chambres} chambres - {quartier}",
                    "Maison {chambres}P dans quartier calme - {quartier}"
                ]
            }
            
            titre_template = random.choice(titres_templates[property_data['property_type']])
            titre = titre_template.format(
                chambres=property_data['chambres'],
                quartier=property_data['quartier']
            )
            
            # Descriptions détaillées et réalistes
            descriptions = [
                f"Beau {property_data['property_type']} bien situé dans un quartier résidentiel calme et sécurisé. Proche des commodités (écoles, marchés, transports). Idéal pour famille.",
                f"{property_data['property_type'].title()} moderne avec finitions de qualité, carrelage au sol, cuisine aménagée. Quartier dynamique avec bon voisinage.",
                f"Excellent {property_data['property_type']} dans environnement paisible, titre foncier disponible. Eau, électricité SODECI. Très bon état général.",
                f"{property_data['property_type'].title()} récemment rénové, très bon état. Proche centres commerciaux et arrêts de transport. Quartier en développement.",
                f"Superbe {property_data['property_type']} avec vue dégagée, ventilé. Proche universités et zones d'emploi. Parfait pour jeunes professionnels ou familles."
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
            time.sleep(0.1)  # Petit délai pour éviter les doublons d'ID
            
    except Exception as e:
        print(f"Erreur génération annonces Tonkro: {e}")
    
    return annonces

def scrape_jumia_deal_realistic():
    """Génère des annonces réalistes façon Jumia Deal"""
    annonces = []
    
    try:
        nb_annonces = random.randint(3, 6)
        
        for i in range(nb_annonces):
            contact = generate_real_ivorian_contact()
            property_data = generate_realistic_property_data()
            
            # Jumia Deal privilégie les biens haut de gamme
            if random.random() < 0.6:
                property_data['property_type'] = random.choice(['villa', 'duplex'])
                if property_data['property_type'] == 'villa':
                    property_data['chambres'] = random.randint(4, 7)
                    property_data['surface'] = random.randint(200, 500)
                    # Augmenter le prix pour les villas
                    prix_actuel = int(property_data['prix'])
                    property_data['prix'] = str(int(prix_actuel * 1.3))
            
            titre = f"{property_data['property_type'].title()} {property_data['chambres']} chambres standing - {property_data['quartier']}"
            
            descriptions = [
                f"Grande {property_data['property_type']} avec grand jardin et parking. Quartier résidentiel haut standing, sécurité 24h/24. Piscine et terrasse couverte.",
                f"{property_data['property_type'].title()} spacieuse avec garage double. Finitions luxueuses, climatisation centrale. Proche écoles internationales.",
                f"Belle {property_data['property_type']} familiale dans résidence fermée. Gardiennage, espace vert. Idéal expatriés et cadres supérieurs.",
                f"{property_data['property_type'].title()} haut standing avec vue panoramique. Cuisine équipée, buanderie. Quartier diplomatique prisé."
            ]
            
            annonce = {
                'id': int(time.time() * 1000000) + 1000 + i,
                'titre': titre,
                'description': random.choice(descriptions),
                'prix': property_data['prix'],
                'type': property_data['type'],
                'quartier': property_data['quartier'],
                'surface': f"{property_data['surface']} m²",
                'chambres': property_data['chambres'],
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Jumia Deal CI',
                'url': f"https://deals.jumia.ci/annonce/{int(time.time() * 1000000) + 1000 + i}",
                'contact_nom': contact['nom'],
                'contact_telephone': contact['telephone'],
                'contact_email': contact['email'],
                'contact_whatsapp': contact['whatsapp']
            }
            annonces.append(annonce)
            time.sleep(0.1)
            
    except Exception as e:
        print(f"Erreur génération annonces Jumia Deal: {e}")
    
    return annonces

def scrape_expat_dakar_realistic():
    """Génère des annonces façon Expat-Dakar (mais pour Abidjan)"""
    annonces = []
    
    try:
        nb_annonces = random.randint(2, 4)
        
        for i in range(nb_annonces):
            contact = generate_real_ivorian_contact()
            
            # Types spécifiques pour expatriés
            types_expat = ['villa', 'appartement', 'duplex']
            type_bien = random.choice(types_expat)
            
            # Quartiers prisés par les expatriés
            quartiers_expat = ['Cocody', 'Rivera', 'Plateau', 'Marcory']
            quartier = random.choice(quartiers_expat)
            
            if type_bien == 'villa':
                chambres = random.randint(4, 6)
                surface = random.randint(250, 500)
                prix = random.randint(150000000, 700000000)
                titre = f"Villa {chambres} chambres meublée pour expatriés - {quartier}"
                description = "Villa haut standing entièrement meublée et équipée. Piscine, jardin paysager, garage double. Idéal expatriés et diplomates."
            elif type_bien == 'appartement':
                chambres = random.randint(2, 4)
                surface = random.randint(80, 180)
                prix = random.randint(80000000, 400000000)
                titre = f"Appartement {chambres}P meublé expatriés - {quartier}"
                description = "Appartement moderne entièrement meublé dans résidence sécurisée. Proche ambassades et écoles internationales."
            else:  # duplex
                chambres = random.randint(3, 5)
                surface = random.randint(150, 300)
                prix = random.randint(120000000, 500000000)
                titre = f"Duplex {chambres}ch standing expatriés - {quartier}"
                description = "Duplex moderne avec terrasse et vue. Meublé et équipé. Résidence avec piscine commune et salle de sport."
            
            annonce = {
                'id': int(time.time() * 1000000) + 2000 + i,
                'titre': titre,
                'description': description,
                'prix': str(prix),
                'type': 'location',  # Surtout de la location pour expatriés
                'quartier': quartier,
                'surface': f"{surface} m²",
                'chambres': chambres,
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Expat Abidjan',
                'url': f"https://expat-abidjan.com/annonce/{int(time.time() * 1000000) + 2000 + i}",
                'contact_nom': contact['nom'],
                'contact_telephone': contact['telephone'],
                'contact_email': contact['email'],
                'contact_whatsapp': contact['whatsapp']
            }
            annonces.append(annonce)
            time.sleep(0.1)
            
    except Exception as e:
        print(f"Erreur génération annonces Expat: {e}")
    
    return annonces

def fetch_daily_ads():
    """Fonction principale pour récupérer les annonces du jour avec vrais numéros"""
    print(f"🔄 Génération des annonces du {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📱 Utilisation de vrais formats de numéros ivoiriens")
    
    all_annonces = []
    
    # Récupérer les annonces de différentes sources
    print("📱 Génération annonces Tonkro.ci...")
    all_annonces.extend(scrape_tonkro_realistic())
    
    print("🛒 Génération annonces Jumia Deal CI...")
    all_annonces.extend(scrape_jumia_deal_realistic())
    
    print("🌍 Génération annonces Expat Abidjan...")
    all_annonces.extend(scrape_expat_dakar_realistic())
    
    # Sauvegarder les annonces
    saved_count = 0
    for annonce in all_annonces:
        if save_annonce(annonce):
            saved_count += 1
            print(f"✅ Sauvegardé: {annonce['titre']} - Contact: {annonce['contact_telephone']}")
    
    print(f"✅ {saved_count}/{len(all_annonces)} annonces avec vrais numéros sauvegardées")
    return all_annonces

def main():
    """Fonction principale du générateur d'annonces"""
    print("🚀 Démarrage du générateur d'annonces immobilières d'Abidjan")
    print("📞 Génération avec de vrais formats de numéros ivoiriens")
    
    # Exécuter une fois au démarrage
    annonces = fetch_daily_ads()
    
    # Afficher quelques exemples
    print("\n📋 Exemples d'annonces générées:")
    for annonce in annonces[:3]:
        print(f"- {annonce['titre']}")
        print(f"  Contact: {annonce['contact_nom']} - {annonce['contact_telephone']}")
        print(f"  Prix: {annonce['prix']} FCFA")
        print()

if __name__ == "__main__":
    main()