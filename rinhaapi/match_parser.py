#!/bin/sh
from os.path import exists

import json
import requests
import numpy as np
import sqlite3
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "rinha.sqlite")

# match_id = "7091254432"

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


global DEBUGGING 
DEBUGGING = True

def get_wards(match_id):

# match_id = "7091254432"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--enable-javascript")
    chrome_options.headless = True
    wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    url = "https://www.dotabuff.com/matches/" + match_id

    wd.get(url)

    wards = []
    elements = wd.find_elements(By.CLASS_NAME, 'color-item-observer-ward') 
    for title in elements:
        amount = title.text
        if amount == '-':
            amount = '0' 
        wards.append(amount)


    sentries = []
    elements = wd.find_elements(By.CLASS_NAME, 'color-item-sentry-ward') 
    for title in elements:
        amount = title.text
        if amount == '-':
              amount = '0' 
        sentries.append(amount)

    wards.pop(11)
    wards.pop(5)
    sentries.pop(11)
    sentries.pop(5)

    return wards, sentries

def parse_match(match_id):
    url = "https://api.opendota.com/api/matches/" + match_id
    response = requests.get(url)
    response_json = response.json()
    wards, sentries = get_wards(match_id)
    # headers = ["lvl", "K", "D", "A", "gold", "xp", "LH", "DN", "heal", "ward", "sentry","hero_dmg", "building_dmg", "hero", "duration"]
    # print(headers)
    cnt = 0
    stats = []
    for player in response_json["players"]:
        stats.append(np.array([player["account_id"], 
                               player["level"], 
                               player["kills"], 
                               player["deaths"], 
                               player["assists"], 
                               player["total_gold"], 
                               player["total_xp"], 
                               player["last_hits"], 
                               player["denies"], 
                               player["hero_healing"], 
                               wards[cnt], 
                               sentries[cnt], 
                               player["hero_damage"], 
                               player["tower_damage"], 
                               player["hero_id"], 
                               response_json["duration"]]))
        cnt += 1

    return np.array(stats)


def save_match(match_id, overwrite):

    if DEBUGGING:
        print("Starting match:", match_id)

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    count = np.max(cur.execute("SELECT COUNT(1) FROM matches WHERE matchid=" + match_id).fetchall())
    

    if not overwrite and count > 0:
        return "Already saved"
        
    if DEBUGGING:
        print("Parsing match..")

    match = parse_match(match_id)

    if DEBUGGING:
        print("Writting to db...")

    for players in match:
        querry = "INSERT INTO matches VALUES (" + match_id + ", "
        for stat in players:
            querry += stat + ", "
        querry += ")"
        querry = querry.replace(", )", ")")
        cur.execute(querry)
    con.commit()

    return "Saved match " + match_id

def stemid64_to_steamid3(old):
    steamid64ident = 76561197960265728
    return (str(int(old) - steamid64ident))

def insert_players():
    players_mu = [["76561198060540379",2,"ldsx", "OD"], 
              ["76561198081160405",5,"Bubigam", "venge"], 
              ["76561198066898764",3,"Lemillion", "legion"], 
              ["76561198071185018",1,"Dark Noise", "ursa"], 
              ["76561198058721793",4,"Raposo", "undy"]]

    players_mnmm = [["76561198014384019",1,"PropsY", "clinkz"], 
                ["76561198077547100",2,"Lhamilson", "pangolier"], 
                ["76561198063574161",5,"tomilsaaa", "oracle"], 
                ["76561198014250817",4,"TED", "omni"], 
                ["76561198131685250",5,"Bunda", "warlock2"],
                ["76561198045809620",3,"JEREMY", "darkseer"],
                ["76561198056818174",3,"Takaboka Navara", "magnus"]]

    players_tm = [["76561198062223936",1,"Fidaler", "void"],
                ["76561198074453179",1,"Reshi", "puck"],
                ["76561198050675168",1,"Kin\'Mar", "under"],
                ["76561198061215930",1,"Matt", "warlock"],
                ["76561198313077410",1,"Tarantula", "mirana"]]
    
    all_teams = [players_mu, players_mnmm, players_tm]

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    if DEBUGGING:
        print("Inserting players:\n")

    team_id = 0
    for team in all_teams:
        for player in team:
            querry = "INSERT INTO players VALUES ("
            for stat in range(len(player)):
                if stat == 0:
                    querry += stemid64_to_steamid3(player[0])
                else:
                    if stat == 2 or stat == 3:
                        querry += "\"" + str(player[stat]) + "\""
                    
                    else:
                        querry += str(player[stat])
                
                querry += ", "
            querry += str(team_id) + ")"
            
            if DEBUGGING:
                print(querry)
            
            cur.execute(querry)
        
        team_id += 1
    con.commit()


def insert_matches():
    matches = ["7063786889",
                "7080828209",
                "7085124719",
                "7070262846", #fase de grupos (1 foi wo, por isso apenas 5 partidas)
                "7104543983",
                "7104584900",
                "7104623704", # MU x Eminence
                "7114897562",
                "7114941107", # MU x Paranoid
                "7060886235",
                "7071648129",
                "7091291913", # fase de grupos (3 foram wo, por isso apenas 3 partidas)
                "7105935084",
                "7105971366",
                "7106012237", # MNMM x STD
                "7062273638",
                "7060921520",
                "7068807049",
                "7070231207",
                "7074524478",
                "7082330201", # fase de grupos
            ]
    for match in matches:
        print(save_match(match, False))

    return


def debug():
    # print(parse_match("7091254432"))
    

    print(save_match("7091254432", False))
    print(save_match("7063786889", False))
    print(save_match("7080828209", False))
    # print(save_match("7091254433", False))

    #insert_players()