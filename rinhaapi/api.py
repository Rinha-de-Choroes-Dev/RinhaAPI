from flask import Flask, jsonify, request
from .performances import *
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello from RinnhaAPI!</p>"

@app.route("/get_player_stats")
def route_get_player_stats():

    player = request.args.get('player')

    if player is None:
        return "<p>No team specified</p>"

    if player.isnumeric():
        stats = get_player_stats(player)
        if len(stats) > 0:
            response = jsonify(stats.tolist())
            return response

    return "<p>Player not found</p>"

@app.route("/get_team_stats")
def route_get_team_stats():

    team = request.args.get('team')

    if team is None:
        return "<p>No team specified</p>"
    
    if team.isnumeric():
        stats = get_team_stats(team)
        if len(stats) > 0:
            # print(stats)
            response = jsonify(stats)
            return response
        
        return "<p>Player from team not found</p>"

    return "<p>Team not found</p>"

@app.route("/get_teams")
def route_get_teams():
    return jsonify(["Mamacos United", "Macaco Não Mata Macaco", "Teamanduá"])