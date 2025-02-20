import os
import pandas as pd
import requests
import logging
import random
from flask import Flask, request, jsonify, render_template
from livereload import Server

app = Flask(__name__)

# URL de votre Azure Function
azure_function_url = 'https://projet10-recommendations.azurewebsites.net/api/reco'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():

    clicks= pd.read_csv('../data/globo/clicks.csv')
    nb_users = len(clicks['user_id'].unique())

    user_id = request.form.get('userID')
    generate = request.form.get('generate')

    if generate:
        user_id = str(random.randint(0, nb_users))  # Générer un user_id aléatoire

    if user_id:
        # Appeler l'Azure Function
        response = requests.get(f"{azure_function_url}?userID={user_id}")
 

        if response.status_code == 200:
            try:
                data = response.json()
                recommendations = data.get("Recommended articles")
                return render_template('index.html', recommendations=recommendations, user_id=user_id)
            except requests.exceptions.JSONDecodeError as e:
                return render_template('index.html', error="Failed to decode JSON response from Azure Function")
        else:
            return render_template('index.html', error="Failed to get recommendations from Azure Function")
    else:
        return render_template('index.html', error="Please enter a userID or generate one")

if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.watch('static/*.*')
    server.watch('templates/*.*')
    server.serve(port=5000, host='0.0.0.0', debug=True)