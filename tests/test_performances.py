import sys
sys.path.insert(1, './../rinhaapi')
import pandas as pd
import numpy as np

from rinhaapi.config import *
from rinhaapi.performances import *

def generate_mock_lane_stat(array):
    mock_won_lane = np.array(array)
    mock_performance = pd.DataFrame(data = mock_won_lane, columns = ['won_lane'])
    lane_stat = PlayerMetrics.compute_lane_stat(mock_performance)
    return lane_stat

def test_compute_lane_stat():

    assert generate_mock_lane_stat([1,1,1,1]) == 1
    assert generate_mock_lane_stat([10,-5,-10,5]) == 0
    assert generate_mock_lane_stat([10,5,5,10]) == 30/4

def test_validate_pint():
    assert validate_pint(5) == 5
    assert validate_pint(0) == 0
    assert validate_pint(10, 8) == -1
    assert validate_pint(-5) == -1
    assert validate_pint(3.14) == -1
    assert validate_pint(3.0) == -1
    assert validate_pint('team') == -1

def test_validate_table():
    assert validate_table(0) == 'matches_rinha3'
    assert validate_table(Tables.PLAYERS_RINHA3) == 'players_rinha3'
    assert validate_table(-1) == -1
    assert validate_table(4) == -1
    assert validate_table(None) == -1

def test_compute_lane_stat():
    performance = pd.DataFrame({'won_lane': [1]})
    assert PlayerMetrics.compute_lane_stat(performance) == 1
    performance = pd.DataFrame({'won_lane': [1, 2, 0]})
    assert PlayerMetrics.compute_lane_stat(performance) == 1
    performance = pd.DataFrame({'won_lane': [-1, -1]})
    assert PlayerMetrics.compute_lane_stat(performance) == -1
    performance = pd.DataFrame({'won_lane': [-2, -1]})
    assert PlayerMetrics.compute_lane_stat(performance) == -3/2

def test_compute_fantasy_points():
    performances = pd.DataFrame({
            'kills': [10, 5, 3],
            'deaths': [2, 1, 0],
            'assists': [5, 3, 2],
            'lh': [200, 150, 100],
            'gpm': [500, 400, 300],
            'xpm': [600, 500, 400],
            'stun': [10, 5, 2],
            'healing': [1000, 500, 200],
            'damage_tower': [5000, 3000, 1000],
            'stacks': [5, 3, 2],
            'wards': [10, 5, 2],
            'sentries': [5, 3, 1]
        })
    expected_output = pd.DataFrame({
        'kills': [3.0, 1.5, 0.9],
        'deaths': [-0.6, -0.3, -0.0],
        'assists': [0.75, 0.45, 0.3],
        'lh': [0.6, 0.45, 0.3],
        'gpm': [2.0, 1.6, 1.2],
        'xpm': [2.4, 2.0, 1.6],
        'stun': [0.004, 0.002, 0.0008],
        'healing': [0.3, 0.15, 0.06],
        'damage_tower': [1.5, 0.9, 0.3],
        'stacks': [2.5, 1.5, 1.0],
        'wards': [3.0, 1.5, 0.6],
        'sentries': [1.5, 0.9, 0.3],
        'sum': [16.954, 10.652, 6.5608]
    })
    output = PlayerMetrics.compute_fantasy_points(performances)
    pd.testing.assert_frame_equal(output, expected_output)