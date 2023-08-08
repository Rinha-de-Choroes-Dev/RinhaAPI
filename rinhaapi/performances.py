import psycopg2
from .config import *
import numpy as np
import os.path
from enum import IntEnum
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

def validate_pint(n, max = 1000):
    if not isinstance(n, int):
        return -1
    if n < 0 or n > max:
        return -1
    return n

class Tables(IntEnum):
    MATCHES_RINHA3 = 0
    PLAYERS_RINHA3 = 1
    MOCK_PLAYERS = 2

table_strings = ['matches_rinha3',
               'players_rinha3',
               'mock_players']

def validate_table(table_idx):
    if not isinstance(table_idx, Tables):
        valid_pint = validate_pint(table_idx, len(table_strings) -1)
        if valid_pint == -1:
            return -1

    return table_strings[table_idx]

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
        
        weighted = performances.copy()[PlayerMetrics.stat_list[:, 0]]
        for stat, weight in PlayerMetrics.stat_list:
            weighted[stat] = weighted[stat].astype('float')*float(weight)

        # weighted['sum'] = weighted.sum(axis='columns')

        return weighted.sum(axis='columns')

    def compute_versat(performances):
        return len(performances.hero_id.unique())/len(performances.hero_id)
    
    def compute_kda(performances):
        return (performances.kills.astype('int32')+performances.assists.astype('int32'))/(performances.deaths.astype('int32') + 1)
    
    def compute_farm(performances):
        w1 = 1
        w2 = 0.8
        return performances.gpm.astype('int32')*w1 + performances.lh.astype('int32')*w2
    
    def compute_tf(performances):
        w1 = 1.2
        w2 = 1
        w3 = 0.5
        return (performances.stun.astype('int32')*w1 + performances.healing.astype('int32')*w2 + performances.damage_hero.astype('int32')*w3)/performances.duration.astype('int32')
    
    def compute_supp(performances):
        w1 = 1000
        w2 = 700
        w3 = 3000
        return (performances.wards.astype('int32')*w1 + performances.sentries.astype('int32')*w2 + performances.stacks.astype('int32')*w3)/performances.duration.astype('int32')
    
    def compute_imp(performances):
        return performances.imp.astype('float')
    
    def compute_card_stats(performances):
        return {"fps": PlayerMetrics.compute_fantasy_points(performances), 
                "imp": PlayerMetrics.compute_imp(performances), 
                "lwr": PlayerMetrics.compute_lane_stat(performances), 
                "vst": PlayerMetrics.compute_versat(performances), 
                "kda": PlayerMetrics.compute_kda(performances), 
                "frm": PlayerMetrics.compute_farm(performances),
                "tfi": PlayerMetrics.compute_tf(performances),
                "sup": PlayerMetrics.compute_supp(performances)}
    
    def compute_card_stats_avg(performances):
        stats = PlayerMetrics.compute_card_stats(performances)
        avg_stats = {}
        
        for k, v in stats.items():
            avg_stats[k] = np.mean(v)

        return avg_stats

def get_player_performances(player, table_idx):

    player = validate_pint(player, 8)
    if player == -1:
        return
    
    table_name = validate_table(table_idx)
    if table_name == -1:
        return

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

def get_team_performances(team, team_table_idx, player_table_idx):
    team = validate_pint(team)
    if team == -1:
        return
    
    team_table = validate_table(team_table_idx)
    if team_table == -1:
        return
    
    player_table = validate_table(player_table_idx)
    if player_table == -1:
        return

    conn = psycopg2.connect(database=db_name,
                    host=db_host,
                    user=db_user,
                    password=db_pass,
                    port=db_port)
    
    cursor = conn.cursor()

    query = "SELECT * FROM " + team_table + " WHERE team=" + str(team)
    cursor.execute(query)

    players = np.array(cursor.fetchall())
    df_players = pd.DataFrame(players, columns = db_headers_team[:, 0])

    query = "SELECT * FROM " + player_table
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

    return df_players, all_performances

def get_all_performances(team_table_idx, player_table_idx):
    team_table = validate_table(team_table_idx)
    if team_table == -1:
        return
    
    player_table = validate_table(player_table_idx)
    if player_table == -1:
        return

    conn = psycopg2.connect(database=db_name,
                    host=db_host,
                    user=db_user,
                    password=db_pass,
                    port=db_port)
    
    cursor = conn.cursor()

    query = "SELECT * FROM " + team_table
    cursor.execute(query)

    players = np.array(cursor.fetchall())
    df_players = pd.DataFrame(players, columns = db_headers_team[:, 0])

    query = "SELECT * FROM " + player_table

    cursor.execute(query)
    stats = np.array(cursor.fetchall())
    df_stats = pd.DataFrame(stats, columns = db_headers_player[:, 0])

    all_performances = []
    for player_id in df_players.steamid:
        all_performances.append(df_stats.loc[df_stats['steamid'] == player_id])

    return df_players, all_performances

def get_all_cards(team_table_idx, player_table_idx):
    df_players, all_performances = get_all_performances(team_table_idx, player_table_idx)
    for i in range(len(all_performances)):
        perf = all_performances[i]
        stats = PlayerMetrics.compute_card_stats_avg(perf)
        print(pd.DataFrame.from_dict(stats))


def debug():

    all_cards = get_all_cards(Tables.PLAYERS_RINHA3, Tables.MATCHES_RINHA3)

    return