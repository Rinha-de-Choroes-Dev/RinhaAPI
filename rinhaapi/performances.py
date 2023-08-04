import psycopg2
from .config import *
import numpy as np
import os.path
from enum import Enum
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

db_headers_player = np.array([ 
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

db_headers_team = np.array([ 
                ['steamid', int],
                ['pos', int],
                ['name', str],
                ['img', str],
                ['team', int]])


class PlayerMetrics():

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

    def compute_lane_stat(performances):

        lanes = performances.won_lane.astype('int32')

        return lanes.sum()/len(lanes)
    
    def compute_fantasy_points(performances):

        
        
        weighted = performances.copy()[stat_list[:, 0]]
        for stat, weight in stat_list:
            weighted[stat] = weighted[stat].astype('float')*float(weight)

        weighted['sum'] = weighted.sum(axis='columns')

        return weighted
        

def get_player_performances(player, table_name):
    conn = psycopg2.connect(database=db_name,
                    host=db_host,
                    user=db_user,
                    password=db_pass,
                    port=db_port)
    
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM " + table_name + " WHERE steamid=\'" + player + "\'")
    
    all_performances = np.array(cursor.fetchall())

    cursor.close()
    conn.close()
    
    df = pd.DataFrame(all_performances, columns = db_headers_player[:, 0])
    for k, v in db_headers_player:
        df[k] = df[k].astype(v)

    return df

def get_team_performances(team, table_name):
    conn = psycopg2.connect(database=db_name,
                    host=db_host,
                    user=db_user,
                    password=db_pass,
                    port=db_port)
    
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM players WHERE team=" + str(team))

    players = np.array(cursor.fetchall())
    df_players = pd.DataFrame(players, columns = db_headers_team[:, 0])

    query = "SELECT * FROM " + table_name
    first = True

    for player_id in df_players.steamid:
        if first:
            query += " WHERE steamid = \'" + player_id + "\'"
            first = False
        else:
            query += " OR steamid = \'" + player_id + "\'"
  
    cursor.execute(query)
    stats = np.array(cursor.fetchall())
    df_stats = pd.DataFrame(stats, columns = db_headers_player[:, 0])

    all_performances = []
    for player_id in df_players.steamid:
        all_performances.append(df_stats.loc[df_stats['steamid'] == player_id])

    return all_performances

def debug():

    # ids = [ ['100274651','Rafael'],
    #         ['110919290','Derig'],
    #         ['98456065','Raposo'],
    #         ['120894677','Bubigam'],
    #         ['106633036','Lemilton']]
    
    # for id, name in ids:
    #     perf = get_player_performances(id)
    #     print("\n" + name)
    #     print(PlayerMetrics.compute_lane_stat(perf))
    #     print(PlayerMetrics.compute_fantasy_points(perf))

    all_performances = get_team_performances(0, "matches_rinha3")

    for perf in all_performances:
        print(PlayerMetrics.compute_lane_stat(perf))
        print(PlayerMetrics.compute_fantasy_points(perf))