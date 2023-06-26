import requests
import json
import os
import sqlite3
from .config import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "rinha.sqlite")
json_path = os.path.join(BASE_DIR, "stratz.json")

def update_league_matches(league_id, use_json=True):

    content = ""

    if (use_json):
        content = json.load(open(json_path))
    else:
        body = f"""
        {{
        league(id: {league_id}){{
            lastMatchDate,
            matches(request: {{isParsed: true, take:2, skip:0}}){{
                id
                durationSeconds
                players {{
                    steamAccountId
                    level
                    kills
                    deaths
                    assists
                    gold
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
        
        for player in match["players"]:
            querry = "INSERT INTO matches VALUES ("
            
            stats = [
                match["id"], 
                player["steamid"], 
                player["level"], 
                player["kills"], 
                player["deaths"], 
                player["assists"], 
                player["gold"], 
                int(player["experiencePerMinute"]*match["duration"]/60), 
                player["numLastHits"], 
                player["numDenies"], 
                player["heroHealing"], 
                player["wards"],
                player["sentries"],
                player["heroDamage"], 
                player["towerDamage"], 
                player["heroId"], 
                match["duration"],
                player["imp"],
                player["stacks"],
                player["won_lane"],
                player["lane"],
                player["award"],
                ]

            for stat in stats:
                querry += str(stat) + ", "

            querry += ")"
            querry = querry.replace(", )", ")")
            # cur.execute(querry)
            print(querry)
    



def debug():
    update_league_matches(15070, True)