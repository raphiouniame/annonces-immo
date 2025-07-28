# database.py
import psycopg2
from psycopg2.extras import RealDictCursor  # Pour obtenir des dictionnaires comme en SQLite
from datetime import datetime
import os
import logging

# Configuration du logging pour aider au débogage
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Récupérer l'URL de la base de données depuis les variables d'environnement
# Render définit automatiquement DATABASE_URL pour les services PostgreSQL liés
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    logger.error("❌ La variable d'environnement DATABASE_URL n'est pas définie.")
    # En développement local, vous pouvez définir une URL par défaut pour PostgreSQL
    # Exemple: DATABASE_URL = "postgresql://user:password@localhost:5432/nom_de_la_db"
    # raise ValueError("DATABASE_URL environment variable is required.")


def get_db_connection():
    """Obtenir une connexion à la base de données PostgreSQL."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required.")
    try:
        # RealDictCursor permet d'accéder aux colonnes par leur nom, comme sqlite3.Row
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except psycopg2.Error as e:
        logger.error(f"❌ Erreur de connexion à la base de données : {e}")
        raise
    # Note: La connexion n'est pas fermée ici, c'est la responsabilité de l'appelant.


def init_database():
    """Initialise la base de données et crée les tables si nécessaire."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Créer la table 'annonces' si elle n'existe pas
        # Note : PostgreSQL est sensible à la casse pour les identifiants non entre guillemets.
        # Il est courant d'utiliser des minuscules.
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS annonces (
            id BIGINT PRIMARY KEY,
            titre TEXT,
            description TEXT,
            prix TEXT,
            type TEXT,
            quartier TEXT,
            surface TEXT,
            chambres INTEGER,
            date_publication DATE,
            date_recuperation TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            source TEXT,
            url TEXT UNIQUE,
            contact_nom TEXT,
            contact_telephone TEXT,
            contact_email TEXT,
            contact_whatsapp TEXT
        );
        '''
        cursor.execute(create_table_query)

        conn.commit()
        logger.info("✅ Base de données initialisée avec succès.")
        return True
    except psycopg2.Error as e:
        logger.error(f"❌ Erreur PostgreSQL lors de l'initialisation de la base de données : {e}")
        # Afficher le message d'erreur détaillé de PostgreSQL
       # e.diag n'est disponible que si l'erreur provient du serveur PostgreSQL
        if hasattr(e, 'diag') and e.diag:
            logger.error(f"   Détails : {getattr(e.diag, 'message_primary', 'N/A')}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur inattendue lors de l'initialisation de la base de données : {e}")
        return False
    finally:
        if conn:
            conn.close()


def save_annonce(annonce):
    """Sauvegarder une annonce dans la base de données PostgreSQL."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Utiliser INSERT ... ON CONFLICT pour éviter les doublons
        # En supposant que 'id' est la clé primaire et doit être unique
        insert_query = '''
        INSERT INTO annonces (
            id, titre, description, prix, type, quartier,
            surface, chambres, date_publication, date_recuperation,
            source, url, contact_nom, contact_telephone,
            contact_email, contact_whatsapp
        ) VALUES (
            %(id)s, %(titre)s, %(description)s, %(prix)s, %(type)s, %(quartier)s,
            %(surface)s, %(chambres)s, %(date_publication)s, %(date_recuperation)s,
            %(source)s, %(url)s, %(contact_nom)s, %(contact_telephone)s,
            %(contact_email)s, %(contact_whatsapp)s
        )
        ON CONFLICT (id) DO NOTHING;
        '''
        # Ajouter le champ date_recuperation à l'annonce si absent
        annonce_to_save = annonce.copy()
        if 'date_recuperation' not in annonce_to_save:
            annonce_to_save['date_recuperation'] = datetime.now()

        cursor.execute(insert_query, annonce_to_save)

        conn.commit()
        # cursor.rowcount est moins fiable avec ON CONFLICT, on vérifie autrement
        # Si ON CONFLICT DO NOTHING ne fait rien, aucune ligne n'est affectée.
        # On considère que si pas d'exception, c'est bon.
        logger.info(f"💾 Annonce '{annonce.get('titre', 'N/A')}' traitée (sauvegardée ou déjà existante).")
        return True

    except psycopg2.Error as e:
        logger.error(f"❌ Erreur PostgreSQL lors de la sauvegarde de l'annonce : {e}")
        if hasattr(e, 'diag') and e.diag:
            logger.error(f"   Détails : {getattr(e.diag, 'message_primary', 'N/A')}")
        logger.error(f"   Annonce concernée (ID): {annonce.get('id', 'N/A')}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur inattendue lors de la sauvegarde de l'annonce : {e}")
        logger.error(f"   Annonce concernée (ID): {annonce.get('id', 'N/A')}")
        return False
    finally:
        if conn:
            conn.close()


def get_annonces_du_jour():
    """Récupérer les annonces du jour depuis PostgreSQL."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        today = datetime.now().date()  # Obtenir la date du jour
        select_query = '''
        SELECT * FROM annonces
        WHERE date_publication = %s
        ORDER BY date_recuperation DESC;
        '''
        cursor.execute(select_query, (today,))

        # cursor.fetchall() retourne une liste de RealDictRow, que l'on peut convertir
        rows = cursor.fetchall()
        annonces = [dict(row) for row in rows]  # Convertir en dictionnaires standard

        # Ajouter une image par défaut si nécessaire (comme dans l'ancien code)
        for annonce in annonces:
            if 'image' not in annonce or not annonce['image']:
                annonce['image'] = 'https://via.placeholder.com/300x200?text=Immobilier'

        logger.info(f"📄 Récupéré {len(annonces)} annonces du jour ({today}).")
        return annonces

    except psycopg2.Error as e:
        logger.error(f"❌ Erreur PostgreSQL lors de la récupération des annonces du jour : {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Erreur inattendue lors de la récupération des annonces du jour : {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_all_annonces():
    """Récupérer toutes les annonces depuis PostgreSQL."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        select_query = '''
        SELECT * FROM annonces
        ORDER BY date_recuperation DESC;
        '''
        cursor.execute(select_query)

        rows = cursor.fetchall()
        annonces = [dict(row) for row in rows]

        # Ajouter une image par défaut si nécessaire
        for annonce in annonces:
            if 'image' not in annonce or not annonce['image']:
                annonce['image'] = 'https://via.placeholder.com/300x200?text=Immobilier'

        logger.info(f"📄 Récupéré {len(annonces)} annonces au total.")
        return annonces

    except psycopg2.Error as e:
        logger.error(f"❌ Erreur PostgreSQL lors de la récupération de toutes les annonces : {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Erreur inattendue lors de la récupération de toutes les annonces : {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_statistiques():
    """Récupérer les statistiques des annonces depuis PostgreSQL."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        stats = {}

        # Total des annonces
        cursor.execute('SELECT COUNT(*) FROM annonces;')
        # Le résultat est un RealDictRow, on accède par clé
        stats['total_annonces'] = cursor.fetchone()['count']

        # Annonces d'aujourd'hui
        today = datetime.now().date()
        cursor.execute('SELECT COUNT(*) FROM annonces WHERE date_publication = %s;', (today,))
        stats['annonces_aujourd_hui'] = cursor.fetchone()['count']

        # Ventes
        cursor.execute("SELECT COUNT(*) FROM annonces WHERE type = 'vente';")
        stats['ventes'] = cursor.fetchone()['count']

        # Locations
        cursor.execute("SELECT COUNT(*) FROM annonces WHERE type = 'location';")
        stats['locations'] = cursor.fetchone()['count']

        # Quartiers actifs
        cursor.execute('SELECT COUNT(DISTINCT quartier) FROM annonces;')
        stats['quartiers_actifs'] = cursor.fetchone()['count']

        logger.info("📈 Statistiques récupérées avec succès.")
        return stats

    except psycopg2.Error as e:
        logger.error(f"❌ Erreur PostgreSQL lors de la récupération des statistiques : {e}")
        if hasattr(e, 'diag') and e.diag:
            logger.error(f"   Détails : {getattr(e.diag, 'message_primary', 'N/A')}")
    except Exception as e:
        logger.error(f"❌ Erreur inattendue lors de la récupération des statistiques : {e}")

    # En cas d'erreur dans les blocs try/except ci-dessus, retourner des valeurs par défaut
    # Ce 'return' ne fait PAS partie d'un 'except', mais est le flot normal de la fonction
    # si une exception non gérée provoque un saut ici, ou si les 'except' se terminent sans 'return'.
    finally:
        if conn:
            conn.close()

    # Si on arrive ici, c'est qu'une exception a été levée et gérée,
    # et que l'on souhaite retourner des valeurs par défaut.
    logger.warning("⚠️ Retour des statistiques par défaut en raison d'une erreur.")
    return {
        'total_annonces': 0,
        'annonces_aujourd_hui': 0,
        'ventes': 0,
        'locations': 0,
        'quartiers_actifs': 0
    }

# Optionnel : Initialiser la base au chargement du module
# if __name__ != "__main__": # Evite l'init si le script est exécuté directement
#     init_database()
