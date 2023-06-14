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

class PlayerMetrics:
    def __init__(self, player):
        if len(player) == 0:
            self.all = []
            return
        
        self.supp = np.mean((player[:, swards]/2000 + player[:, ssentries] + player[:, shealing])/player[:, sduration])
        
        self.kda = np.mean((player[:, skills]+player[:, sassists])/(player[:, sdeaths] + 1))
        
        self.farm = np.mean(player[:, sgold]/player[:, sduration])
        
        self.versat = len(np.unique(player[:, shero_id]))/len(player[:, shero_id])
        
        self.fight = np.mean((player[:, skills] + player[:, sassists] + player[:, sdamage_hero]/2000)/player[:, sduration])
        
        self.push = np.mean(player[:, sdamage_tower]/player[:, sduration])
        
        self.all = np.array([self.supp, self.kda, self.farm, self.versat, self.fight, self.push])


def generate_stats(player):
    con = sqlite3.connect("./rinhaapi/rinha.sqlite")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM matches WHERE steamid=" + player)
    
    all_performances = np.array(res.fetchall())

    player_metrics = PlayerMetrics(all_performances)
    
    return player_metrics

def get_max_stats():
    con = sqlite3.connect("./rinhaapi/rinha.sqlite")
    cur = con.cursor()
    res = cur.execute("SELECT steamid FROM players")
    players = res.fetchall()

    players_stats = []

    for player in players:
        stats = generate_stats(str(player[0])).all
        if len(stats) > 0:
            players_stats.append(stats)

    players_stats = np.array(players_stats)

    return np.max(players_stats, axis=0)
    
def get_player_stats(player, max=[]):
    if len(max) == 0:
        max = get_max_stats()
    player_stats = generate_stats(player)

    if len(player_stats.all) == 0:
        return []

    return np.rint(player_stats.all/max*100)

psteamid = 0
ppos = 1
pname = 2
pimg = 3
pteam = 4

def get_team_stats(team_id):
    

    con = sqlite3.connect("./rinhaapi/rinha.sqlite")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM players WHERE team == " + team_id)
    team = res.fetchall()

    max = get_max_stats()
    team_stats = []

    for player in team:
        player_stats = get_player_stats(str(player[psteamid]), max).tolist()

        player_dict = {
            'steamid': player[psteamid],
            'pos': player[ppos],
            'name': player[pname],
            'img': player[pimg],
            'team': player[pteam],
            'stats': player_stats,
        }

        team_stats.append(player_dict)

    return team_stats
    

def debug():
    print(get_team_stats("0"))

