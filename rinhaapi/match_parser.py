#!/bin/sh
from os.path import exists

import json
import requests
import numpy as np
import sqlite3

# match_id = "7091254432"

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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

# def save_match(m, overwrite):
#     filename = "ReplaysDB/" + m.match_id + ".csv"
#     if not overwrite:
#         if exists(filename):
#             print(m.match_id + " - already saved")
#             return
    
#     performances = get_stats(m)
    
#     f = open(filename, "w")
#     header = "Match,Source,Id,LVL,K,D,A,G,XP,LH,DN,Heal,Ward,Sentry,HDamage,TDamage,Hero,Duration\n"
#     f.write(header)
#     for p in  performances:
#         line = m.match_id + "," + m.match_source + ","
#         for stat in p:
#             line += stat + ","
#         line = line[:-1] + "\n"
#         f.write(line)
#     f.close()
#     print(m.match_id + " - saved")

def save_match(match_id, overwrite):

    if DEBUGGING:
        print("Starting match:", match_id)

    con = sqlite3.connect("./rinhaapi/matches.sqlite")
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


def debug():
    # print(parse_match("7091254432"))
    global DEBUGGING 
    DEBUGGING = True

    print(save_match("7091254432", False))
    print(save_match("7063786889", False))
    print(save_match("7080828209", False))
    # print(save_match("7091254433", False))