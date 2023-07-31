import requests
import json
import os
import sqlite3
from .config import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "rinha.sqlite")
json_path = os.path.join(BASE_DIR, "stratz.json")

print(db_path)

def get_wards(player, ward_or_sentry):
    wards = 0
    for ward in player["stats"]["wards"]:
        if ward["type"] == ward_or_sentry:
            wards += 1 
                           
    return wards

def get_won_lane(player, match, player_number):
    lane = player["lane"]
    team = 0 if player_number <= 5 else 1
    
    outcome = match["midLaneOutcome"]

    if (lane == "OFF_LANE" and team == 0) or (lane == "SAFE_LANE" and team == 1):
        outcome = match["topLaneOutcome"]

    elif (lane == "OFF_LANE" and team == 1) or (lane == "SAFE_LANE" and team == 0):
        outcome = match["bottomLaneOutcome"]

    else:
        outcome = match["midLaneOutcome"]
    
    if "TIE" in outcome: 
        return 0
    
    result = 1

    if "STOMP" in outcome:
        result = 2

    if (team == 0 and "RADIANT" in outcome) or (team == 1 and "DIRE" in outcome):
        return result
    else:
        return -1*result

    return victory

def update_league_matches(league_id, use_json=True):

    content = ""

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    res = cur.execute("SELECT COUNT(matchid) FROM matches")
    
    skips = int(res.fetchall()[0][0]/10)

    if (use_json):
        content = json.load(open(json_path))
    else:
        body = f"""
        {{
        league(id: {league_id}){{
            lastMatchDate,
            matches(request: {{isParsed: true, take:100, skip:{skips}}}){{
                id
                durationSeconds
                players {{
                    steamAccountId
                    level
                    kills
                    deaths
                    assists
                    goldPerMinute
                    experiencePerMinute
                    numLastHits
                    numDenies
                    heroHealing
                    heroDamage
                    towerDamage
                    heroId
                    imp
                    award
                    lane
                    stats {{
                    campStack
                        wards{{
                            type
                        }}
                        heroDamageReport{{
                            dealtTotal{{
                                stunDuration
                                }}
                            }}
                    }}
                }}
                bottomLaneOutcome
                topLaneOutcome
                midLaneOutcome      
            }}
        }}
        }}
        """

        url = "https://api.stratz.com/graphql"
        headers = {"Authorization": f"Bearer {stratz_token}", 'content-type': 'application/json'}
        response = requests.post(url=url, json={"query": body}, headers=headers)
        content = json.loads(response.content)

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    for match in content["data"]["league"]["matches"]:
        player_number = 0
        print(match["id"])
        for player in match["players"]:
            player_number += 1
            querry = "INSERT INTO matches VALUES ("
            
            stats = []
            if (match["bottomLaneOutcome"] is None):
                stats = [
                    match["id"], 
                    player["steamAccountId"], 
                    player["level"], 
                    player["kills"], 
                    player["deaths"], 
                    player["assists"], 
                    player["goldPerMinute"], 
                    player["experiencePerMinute"], 
                    player["numLastHits"], 
                    player["numDenies"], 
                    player["heroHealing"], 
                    0,
                    0,
                    player["heroDamage"], 
                    player["towerDamage"], 
                    player["heroId"], 
                    match["durationSeconds"],
                    0,
                    0,
                    0,
                    0,  
                ]
            else:
                stats = [
                    match["id"], 
                    player["steamAccountId"], 
                    player["level"], 
                    player["kills"], 
                    player["deaths"], 
                    player["assists"], 
                    player["goldPerMinute"], 
                    player["experiencePerMinute"], 
                    player["numLastHits"], 
                    player["numDenies"], 
                    player["heroHealing"], 
                    get_wards(player, 1),
                    get_wards(player, 0),
                    player["heroDamage"], 
                    player["towerDamage"], 
                    player["heroId"], 
                    match["durationSeconds"],
                    player["imp"],
                    player["stats"]["campStack"][-1],
                    get_won_lane(player, match, player_number),
                    player["stats"]["heroDamageReport"]["dealtTotal"]["stunDuration"],
                    ]

            for stat in stats:
                querry += str(stat) + ", "

            if (player["lane"] is None):
                querry += "\"NULL\", "
                querry += "\"NULL\""
            else:
                querry += "\"" + player["lane"] + "\", "
                querry += "\"" + player["award"] + "\""
            querry += ")"
            cur.execute(querry)

    con.commit()



def debug():
    update_league_matches(15070, False)