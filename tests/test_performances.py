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

def test_compute_fantasy_points():
    assert PlayerMetrics.stat_list == 0