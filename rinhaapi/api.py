from flask import Flask, jsonify, request
from .performances import *

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

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
        print(stats)
        response = jsonify(stats)
        return response

    return "<p>Team not found</p>"