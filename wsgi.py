#!/usr/bin/env python3
"""
Point d'entrée WSGI pour l'application Flask
Utilisé par Gunicorn pour servir l'application sur Render
"""

import os
import sys

# Ajouter le répertoire courant au PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))

from app import app

# Initialiser la base de données au démarrage
from app import ensure_database_initialized
ensure_database_initialized()

if __name__ == "__main__":
    # Pour les tests locaux
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)