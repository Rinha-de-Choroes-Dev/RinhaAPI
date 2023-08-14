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
                ['team_id', int],
                ['name', str],
                ['lane', str],
                ['award', str],
                ['position', str],
                ['team_name', str],
                ])


def validate_pint(n, max = -1):
    if not isinstance(n, int):
        return -1
    
    if n < 0:
        return -1
    
    if max > 0 and n > max:
        return -1

    return n

class Tables(IntEnum):
    MATCHES_RINHA3 = 0
    MATCHES_RINHA4_DIV1 = 1
    MATCHES_RINHA4_DIV2 = 2

table_strings = ['matches_rinha3',
               'matches_rinha4_div1',
               'matches_rinha4_div2']

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

    player = validate_pint(player)
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

def get_team_performances(team, player_table_idx):
    team = validate_pint(team)
    if team == -1:
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

    query = "SELECT * FROM " + player_table + " WHERE team_id=" + str(team)
    first = True
  
    cursor.execute(query)
    stats = np.array(cursor.fetchall())
    df_stats = pd.DataFrame(stats, columns = db_headers_player[:, 0])

    player_ids = pd.unique(df_stats['steamid'])

    all_performances = []
    for player_id in player_ids:
        all_performances.append(df_stats.loc[df_stats['steamid'] == player_id])

    return all_performances

def get_all_performances(player_table_idx):
    
    player_table = validate_table(player_table_idx)
    if player_table == -1:
        return

    conn = psycopg2.connect(database=db_name,
                    host=db_host,
                    user=db_user,
                    password=db_pass,
                    port=db_port)
    
    cursor = conn.cursor()
    query = "SELECT * FROM " + player_table

    cursor.execute(query)
    stats = np.array(cursor.fetchall())
    df_stats = pd.DataFrame(stats, columns = db_headers_player[:, 0])
    
    player_ids = pd.unique(df_stats['steamid'])

    all_performances = []
    for player_id in player_ids:
        all_performances.append(df_stats.loc[df_stats['steamid'] == player_id])

    return all_performances

def generate_position(position):
    return int(position[-1])
     

def get_all_cards(player_table_idx):
    all_performances = get_all_performances(player_table_idx)
    stats_list = []
    for i in range(len(all_performances)):
        perf = all_performances[i]
        stats = PlayerMetrics.compute_card_stats_avg(perf)
        stats["name"] = all_performances[i].name.iloc[-1]
        stats["pos"] = generate_position(all_performances[i].position.iloc[-1])
        stats["team_id"] = all_performances[i].team_id.iloc[-1]
        stats["team_name"] = all_performances[i].team_name.iloc[-1]
        stats_list.append(stats)
    
    df_stats = pd.DataFrame(stats_list)
    
    return df_stats

def get_all_cards_normalized(player_table_idx):
    df_stats = get_all_cards(player_table_idx)
    df_stats.iloc[:, :8] = (df_stats.iloc[:, :8] - df_stats.iloc[:, :8].min())/(df_stats.iloc[:, :8].max() - df_stats.iloc[:, :8].min())*100 # min max normalization
    df_stats.iloc[:, :8] = df_stats.iloc[:, :8].fillna(100).round(1)

    return df_stats


def debug():

    # df_players, df_normalized = get_all_cards_normalized(Tables.PLAYERS_RINHA3, Tables.MATCHES_RINHA3)

    # print(df_normalized)

    print("\nRDC 3 ED")
    print(get_all_cards_normalized(Tables.MATCHES_RINHA3))

    print("\nRDC 4 ED - Div 1")
    print(get_all_cards_normalized(Tables.MATCHES_RINHA4_DIV1))

    print("\nRDC 4 ED - Div 1")
    print(get_all_cards_normalized(Tables.MATCHES_RINHA4_DIV2))

    return