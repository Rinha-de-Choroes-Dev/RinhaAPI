import sqlite3
import numpy as np

smatchid = 0
ssteamid = 1
slevel = 2
skills = 3
sdeaths = 4
sassists = 5
sgold = 6
sxp = 7
slh = 8
sdn = 9
shealing = 10
swards = 11
ssentries = 12
sdamage_hero = 13
sdamage_tower = 14
shero_id = 15
sduration = 16

# def supp(player):
#     return np.mean((player[:, 11].astype(float)/2000 + player[:, 12].astype(float) + player[:, 13].astype(float))/player[:, 17].astype(float)*10000)

# def kda(player):
#     return np.mean((player[:, 4].astype(float)+player[:, 6].astype(float))/(player[:, 5].astype(float) + 1))*10

# def farm(player):
#     return np.mean(player[:, 9].astype(float)/player[:, 17].astype(float))*1000

# def versat(player):
#     return len(np.unique(player[:, 16]))/len(player[:, 16])*100

# def fight(player):
#     return np.mean((player[:, 4].astype(float) + player[:, 6].astype(float) + player[:, 14].astype(float)/2000)/player[:, 17].astype(float))*6000

# def push(player):
#     return np.mean(player[:, 15].astype(float)/player[:, 17].astype(float))*35

# def all_metrics(player):
#     return np.rint(np.array([supp(player), kda(player), farm(player), versat(player), fight(player), push(player)]))


def generate_stats(player):
    con = sqlite3.connect("./rinhaapi/matches.sqlite")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM matches WHERE steamid=" + player)
    
    all_performances = np.array(res.fetchall())

    player_performances = {}

    for i in range(len(all_performances)):
        header_list



def debug():
    generate_stats("100274651")
