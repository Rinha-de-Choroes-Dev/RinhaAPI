import sys
sys.path.insert(1, './../rinhaapi')
import pandas as pd

from rinhaapi.config import *
from rinhaapi.match_parser import *

mock_player = pd.read_csv("./tests/player.csv")


def test_get_wards():
    
    cnt = 0
    ward_list1 = []
    ward_list2 = []

    for _ in mock_player["wards"]:
        cnt += 1
        wtype1 = 0
        wtype2 = 0
        
        if cnt > 2:
            wtype1 = 1

        if cnt > 4:
            wtype2 = 1
        
        temp_ward1 = {"type": wtype1}
        temp_ward2 = {"type": wtype2}
        
        ward_list1.append(temp_ward1)
        ward_list2.append(temp_ward2)

    mock_wards1 = {"stats": {"wards": ward_list1}}
    mock_wards2 = {"stats": {"wards": ward_list2}}


    assert get_wards(mock_wards1) == 2
    assert get_wards(mock_wards1, 0) == 2
    assert get_wards(mock_wards1, 1) == 8
    assert get_wards(mock_wards2, 0) == 4
    assert get_wards(mock_wards2, 1) == 6

def test_get_won_lane():

    mock_match1 = {"topLaneOutcome" : "TIE",
                   "bottomLaneOutcome" : "TIE",
                   "midLaneOutcome": "TIE"}

    mock_match2 = {"topLaneOutcome" : "RADIANT_STOMP",
                   "bottomLaneOutcome" : "RADIANT",
                   "midLaneOutcome": "DIRE"}

    mock_match3 = {"topLaneOutcome" : "DIRE_STOMP",
                   "bottomLaneOutcome" : "RADIANT_STOMP",
                   "midLaneOutcome": "DIRE"}
    
    mock_player1 = {"lane": "OFF_LANE"}
    mock_player2 = {"lane": "MID_LANE"}
    mock_player3 = {"lane": "SAFE_LANE"}

    assert get_won_lane(mock_player1, mock_match1, 1) == 0
    assert get_won_lane(mock_player1, mock_match2, 4) == 2
    assert get_won_lane(mock_player1, mock_match3, 3) == -2
    assert get_won_lane(mock_player2, mock_match1, 8) == 0
    assert get_won_lane(mock_player2, mock_match2, 3) == -1
    assert get_won_lane(mock_player2, mock_match2, 7) == 1
    assert get_won_lane(mock_player3, mock_match3, 9) == 2

def test_update_league_matches():
    conn = psycopg2.connect(database=db_name,
                    host=db_host,
                    user=db_user,
                    password=db_pass,
                    port=db_port)
    
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(matchid) FROM matches_rinha3")

    lines = int(cursor.fetchall()[0][0])

    cursor.close()
    conn.close()
    
    update_league_matches(15070, "matches_rinha3")

    conn = psycopg2.connect(database=db_name,
                    host=db_host,
                    user=db_user,
                    password=db_pass,
                    port=db_port)
    
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(matchid) FROM matches_rinha3")

    lines2 = int(cursor.fetchall()[0][0])

    cursor.close()
    conn.close()

    assert lines == lines2


