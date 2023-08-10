import requests
import json
import os
from .config import *
import psycopg2
from .performances import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_wards(player, ward_or_sentry=0):

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
    
def get_team_id(match, player_number):
    team = 0 if player_number <= 5 else 1
    if team == 0:
        return match["radiantTeamId"]
    
    return match["direTeamId"]

def generate_name(bulshit_name):
    normal_string="".join(ch for ch in bulshit_name if ch.isalnum())
    return "\'" + normal_string+ "\'"

table_columns = ["matchid",
                "steamid",
                "level",
                "kills",
                "deaths",
                "assists",
                "gpm",
                "xpm",
                "lh",
                "dn",
                "healing",
                "wards",
                "sentries",
                "damage_hero",
                "damage_tower",
                "hero_id",
                "duration",
                "imp",
                "stacks",
                "won_lane",
                "stun",
                "team_id",
                "name",
                "lane",
                "award"
                ]

def update_league_matches(league_id, table_idx):
    table_name = validate_table(table_idx)
    if table_name == -1:
        return

    content = ""

    conn = psycopg2.connect(database=db_name,
                    host=db_host,
                    user=db_user,
                    password=db_pass,
                    port=db_port)
    
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(matchid) FROM " + table_name)

    skips = int(cursor.fetchall()[0][0]/10)

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
                steamAccount{{
                    name
                }}
            }}
            bottomLaneOutcome
            topLaneOutcome
            midLaneOutcome
            radiantTeamId
            direTeamId      
        }}
    }}
    }}
    """

    url = "https://api.stratz.com/graphql"
    headers = {"Authorization": f"Bearer {stratz_token}", 'content-type': 'application/json'}
    response = requests.post(url=url, json={"query": body}, headers=headers)
    content = json.loads(response.content)


    for match in content["data"]["league"]["matches"]:
        player_number = 0
        print(match["id"])
        for player in match["players"]:
            player_number += 1
            querry = "INSERT INTO " + table_name + " ("

            for column in table_columns:
                querry += column + ","

            querry += ") VALUES ("

            querry = querry.replace(",)", ")")
            
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
                    get_team_id(match, player_number),
                    generate_name(player["steamAccount"]["name"])
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
                    get_team_id(match, player_number),
                    generate_name(player["steamAccount"]["name"])
                    ]

            for stat in stats:
                querry += str(stat) + ", "

            if (player["lane"] is None):
                querry += "\'NULL\', "
                querry += "\'NULL\'"
            else:
                querry += "\'" + player["lane"] + "\', "
                querry += "\'" + player["award"] + "\'"
            querry += ")"
            # print(querry)
            # return
            cursor.execute(querry)
    
    conn.commit()
    cursor.close()
    conn.close()


def debug():
    update_league_matches(15070, Tables.MATCHES_RINHA3)