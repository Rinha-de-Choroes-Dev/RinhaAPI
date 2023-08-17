from flask import Flask, jsonify, request
from .performances import *
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

leagues = len(table_strings)
last_update = [-1]*leagues
league_dbs = {}

@app.route("/")
def hello_world():
    return "<p>Hello from RinnhaAPI!</p>"

@app.route("/get_league_card_stats")
def route_get_player_stats():

    league = 0
    try:
        league = int(request.args.get('league'))
    
    except:
       return "<p>League must be a number</p>" 

    if league is None:
        return "<p>No league specified</p>"
    

    update = False
    if last_update[league] == -1:
        update = True
    else:
        deltatime = datetime.now() - last_update[league]
        print(deltatime)
        if deltatime > timedelta(hours=6):
            update = True
    
    if update:
        print("Update")
        stats = get_all_cards_normalized(league)
        if stats is not None:
            league_dbs[league] = stats
            last_update[league] = datetime.now()
    else:
        print("Old")
        stats = league_dbs[league]
        

    if stats is not None:
        response = stats.to_json()
        return response

    return "<p>League not found</p>"
