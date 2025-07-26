import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
from database import save_annonce

class RealEstateScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def scrape_all_sources(self):
        """Scraper toutes les sources disponibles"""
        all_annonces = []
        
        print("🔍 Scraping des sites d'annonces réels...")
        
        # Scraper différentes sources
        all_annonces.extend(self.scrape_tonkro())
        time.sleep(2)  # Respecter les serveurs
        
        all_annonces.extend(self.scrape_jumia_house())
        time.sleep(2)
        
        all_annonces.extend(self.scrape_facebook_marketplace())
        time.sleep(2)
        
        return all_annonces

    def scrape_tonkro(self):
        """Scraper Tonkro.ci - le vrai site"""
        print("📱 Scraping Tonkro.ci...")
        annonces = []
        
        try:
            # URLs des différentes catégories
            urls = [
                "https://tonkro.ci/categorie/immobilier/vente-maison-villa",
                "https://tonkro.ci/categorie/immobilier/location-maison-villa",
                "https://tonkro.ci/categorie/immobilier/vente-appartement",
                "https://tonkro.ci/categorie/immobilier/location-appartement"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=15)
                    if response.status_code != 200:
                        continue
                        
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Chercher les liens vers les annonces individuelles
                    # Ces sélecteurs peuvent changer selon la structure du site
                    annonce_links = soup.find_all('a', href=re.compile(r'/annonce/'))
                    
                    for link in annonce_links[:5]:  # Limiter à 5 par catégorie
                        annonce_url = link.get('href')
                        if not annonce_url.startswith('http'):
                            annonce_url = 'https://tonkro.ci' + annonce_url
                        
                        annonce_data = self.scrape_single_tonkro_ad(annonce_url)
                        if annonce_data:
                            annonces.append(annonce_data)
                            time.sleep(1)  # Pause entre chaque annonce
                            
                except Exception as e:
                    print(f"Erreur URL {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Erreur scraping Tonkro: {e}")
        
        print(f"✅ {len(annonces)} annonces récupérées de Tonkro.ci")
        return annonces

    def scrape_single_tonkro_ad(self, url):
        """Scraper une annonce individuelle de Tonkro"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraire les informations (à adapter selon la vraie structure)
            titre = self.extract_text(soup, ['h1', '.title', '.ad-title'])
            description = self.extract_text(soup, ['.description', '.ad-description', 'p'])
            prix = self.extract_price(soup)
            
            # Extraire les contacts - C'EST LE PLUS IMPORTANT
            contact_info = self.extract_contact_info(soup)
            
            # Informations de base
            quartier = self.extract_quartier(titre + " " + description)
            type_annonce = self.extract_type(titre + " " + description)
            surface = self.extract_surface(description)
            chambres = self.extract_chambres(description)
            
            if not contact_info.get('telephone') and not contact_info.get('email'):
                return None  # Pas de contact = pas d'annonce valide
            
            return {
                'id': int(time.time() * 1000000),
                'titre': titre or "Annonce immobilière",
                'description': description or "",
                'prix': prix or "Prix sur demande",
                'type': type_annonce,
                'quartier': quartier,
                'surface': surface,
                'chambres': chambres,
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Tonkro.ci',
                'url': url,
                'contact_nom': contact_info.get('nom', 'Propriétaire'),
                'contact_telephone': contact_info.get('telephone', ''),
                'contact_email': contact_info.get('email', ''),
                'contact_whatsapp': contact_info.get('whatsapp', contact_info.get('telephone', ''))
            }
            
        except Exception as e:
            print(f"Erreur scraping annonce {url}: {e}")
            return None

    def extract_contact_info(self, soup):
        """Extraire les vraies informations de contact"""
        contact_info = {}
        
        # Chercher dans le texte complet de la page
        text_content = soup.get_text()
        
        # Patterns pour les numéros ivoiriens
        phone_patterns = [
            r'\+225\s*[0-9]{2}\s*[0-9]{2}\s*[0-9]{2}\s*[0-9]{2}',
            r'225\s*[0-9]{2}\s*[0-9]{2}\s*[0-9]{2}\s*[0-9]{2}',
            r'[0-9]{2}\s*[0-9]{2}\s*[0-9]{2}\s*[0-9]{2}',
            r'[0-9]{8}'
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text_content)
            if matches:
                # Nettoyer le numéro
                phone = re.sub(r'\s+', '', matches[0])
                if not phone.startswith('+225'):
                    if phone.startswith('225'):
                        phone = '+' + phone
                    elif len(phone) == 8:
                        phone = '+225' + phone
                
                contact_info['telephone'] = phone
                contact_info['whatsapp'] = phone
                break
        
        # Chercher l'email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text_content)
        if emails:
            contact_info['email'] = emails[0]
        
        # Chercher le nom dans les balises de contact
        name_selectors = ['.contact-name', '.advertiser-name', '.seller-name', '.author']
        for selector in name_selectors:
            name_elem = soup.select_one(selector)
            if name_elem:
                contact_info['nom'] = name_elem.get_text().strip()
                break
        
        return contact_info

    def scrape_jumia_house(self):
        """Scraper Jumia House CI"""
        print("🏠 Scraping Jumia House...")
        annonces = []
        
        try:
            url = "https://house.jumia.ci/appartements-a-louer/abidjan"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Adapter selon la structure de Jumia House
                # Similar logic as Tonkro
                pass
                
        except Exception as e:
            print(f"Erreur Jumia House: {e}")
        
        return annonces

    def scrape_facebook_marketplace(self):
        """Scraper Facebook Marketplace (plus complexe)"""
        print("📘 Tentative Facebook Marketplace...")
        # Facebook nécessite une approche différente (authentification, JavaScript)
        # Pour l'instant, on skip
        return []

    # Fonctions utilitaires
    def extract_text(self, soup, selectors):
        """Extraire du texte avec plusieurs sélecteurs possibles"""
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        return ""

    def extract_price(self, soup):
        """Extraire le prix"""
        price_selectors = ['.price', '.prix', '.cost', '.amount']
        for selector in price_selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        
        # Chercher dans le texte avec regex
        text = soup.get_text()
        price_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:millions?|M)\s*FCFA',
            r'(\d+(?:\s*\d+)?)\s*FCFA',
            r'Prix\s*:?\s*(\d+(?:\s*\d+)*)'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0] + " FCFA"
        
        return "Prix sur demande"

    def extract_quartier(self, text):
        """Extraire le quartier"""
        quartiers = [
            'Plateau', 'Cocody', 'Treichville', 'Marcory', 'Yopougon',
            'Rivera', 'Bingerville', 'Anyama', 'Koumassi', 'Port-Bouet',
            'Adjamé', 'Abobo', 'Attécoubé', 'Songon', 'Bassam'
        ]
        
        text_lower = text.lower()
        for quartier in quartiers:
            if quartier.lower() in text_lower:
                return quartier
        return "Abidjan"

    def extract_type(self, text):
        """Extraire le type (vente/location)"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['location', 'louer', 'à louer', 'rent']):
            return 'location'
        return 'vente'

    def extract_surface(self, text):
        """Extraire la surface"""
        surface_pattern = r'(\d+)\s*m[²2]'
        matches = re.findall(surface_pattern, text)
        if matches:
            return f"{matches[0]} m²"
        return ""

    def extract_chambres(self, text):
        """Extraire le nombre de chambres"""
        chambres_patterns = [
            r'(\d+)\s*chambres?',
            r'(\d+)\s*ch\b',
            r'(\d+)\s*pièces?',
            r'(\d+)P'
        ]
        
        for pattern in chambres_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                return int(matches[0])
        return 0


def fetch_daily_ads():
    """Fonction principale pour récupérer les vraies annonces"""
    scraper = RealEstateScraper()
    
    print(f"🚀 Début du scraping des vraies annonces - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Récupérer les annonces
    annonces = scraper.scrape_all_sources()
    
    # Sauvegarder seulement les annonces avec des contacts
    saved_count = 0
    for annonce in annonces:
        if annonce.get('contact_telephone') or annonce.get('contact_email'):
            if save_annonce(annonce):
                saved_count += 1
        else:
            print(f"❌ Annonce ignorée (pas de contact): {annonce.get('titre', 'Sans titre')}")
    
    print(f"✅ {saved_count}/{len(annonces)} vraies annonces sauvegardées")
    return annonces


if __name__ == "__main__":
    # Test du scraper
    annonces = fetch_daily_ads()
    for annonce in annonces:
        print(f"📋 {annonce['titre']} - Contact: {annonce.get('contact_telephone', 'N/A')}")