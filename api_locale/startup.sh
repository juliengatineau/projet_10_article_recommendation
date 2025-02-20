#!/bin/bash

# Activer l'environnement virtuel si nécessaire
# source venv/bin/activate

# Exporter les variables d'environnement nécessaires
export FLASK_APP=app.py
export FLASK_ENV=development

# Lancer l'application Flask
flask run