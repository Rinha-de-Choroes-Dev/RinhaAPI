import sqlite3
import numpy as np
import os.path
from enum import Enum
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "rinha.sqlite")

class PlayerMetrics:
    def compute_lane_stat(performances):

        lanes = performances.won_lane

        return lanes.sum()/len(lanes)
    
    def compute_fantasy_points(performances):

        stat_list = np.array([
                     ['kills', 0.3],
                     ['deaths', -0.3], 
                     ['assists', 0.15],
                     ['lh', 0.003],
                     ['gpm', 0.004],
                     ['xpm', 0.004],
                     ['stun', 0.0004],
                     ['healing', 0.0003],
                     ['damage_tower', 0.0003],
                     ['stacks', 0.5],
                     ['wards', 0.3],
                     ['sentries', 0.3]
                     ])
        
        weighted = performances.copy()[stat_list[:, 0]]
        for stat, weight in stat_list:
            weighted[stat] = weighted[stat]*float(weight)

        weighted['sum'] = weighted.sum(axis='columns')

        return weighted
        

def get_player_performances(player):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    res = cur.execute("SELECT * FROM matches WHERE steamid=" + player)
    
    all_performances = np.array(res.fetchall())

    headers = np.array([ 
                ['matchid', int],
                ['steamid', int],
                ['level', int],
                ['kills', int],
                ['deaths', int],
                ['assists',int],
                ['gpm', int],
                ['xpm', int],
                ['lh', int],
                ['dn', int],
                ['healing', int],
                ['wards', int],
                ['sentries', int],
                ['damage_hero', int],
                ['damage_tower', int],
                ['hero_id', int],
                ['duration', int],
                ['imp', int],
                ['stacks', int],
                ['won_lane', int],
                ['stun', int],
                ['lane', str],
                ['award', str]
                ])
    
    df = pd.DataFrame(all_performances, columns = headers[:, 0])
    for k, v in headers:
        df[k] = df[k].astype(v)

    return df

def debug():

    ids = [ ['100274651','Rafael'],
            ['110919290','Derig'],
            ['98456065','Raposo'],
            ['120894677','Bubigam'],
            ['106633036','Lemilton']]
    
    for id, name in ids:
        perf = get_player_performances(id)
        print("\n" + name)
        print(PlayerMetrics.compute_lane_stat(perf))
        print(PlayerMetrics.compute_fantasy_points(perf))