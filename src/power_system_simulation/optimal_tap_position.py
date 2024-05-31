# Load dependencies and functions from graph_processing
import copy
from typing import List, Tuple
import networkx as nx

# Load dependencies and functions from calculation_module
import pandas as pd
from power_grid_model import CalculationMethod, CalculationType, PowerGridModel, initialize_array, validation
from power_grid_model.utils import json_deserialize, json_serialize_to_file
from power_grid_model.validation import ValidationException, assert_valid_batch_data, assert_valid_input_data

from calculation_module import *
from graph_processing import *


def optimal_tap_position(input_network_data: str):

    with open(input_network_data) as fp:
        input_data = json_deserialize(fp.read())

    pos_min = np.take(input_data['transformer']['tap_min'],0)
    pos_max = np.take(input_data['transformer']['tap_max'],0)

    for tap_pos in range(pos_max, pos_min+1):
        input_data['transformer']['tap_pos'] = tap_pos
        print(input_data['transformer']['tap_pos'])

    return


input_network_data = "../data/input_3_test/input_network_data.json"

optimal_tap_position(input_network_data) 
