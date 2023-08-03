import sys
sys.path.insert(1, './../rinhaapi')
import pandas as pd

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


    assert get_wards() == -1
    assert get_wards(mock_wards1) == 2
    assert get_wards(mock_wards1, 0) == 2
    assert get_wards(mock_wards1, 1) == 8
    assert get_wards(mock_wards2, 0) == 4
    assert get_wards(mock_wards2, 1) == 6

