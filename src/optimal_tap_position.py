# Load dependencies and functions from graph_processing
import copy
from typing import List, Tuple
import networkx as nx

from power_system_simulation.graph_processing import *

# Load dependencies and functions from calculation_module
import pandas as pd 
from power_grid_model import CalculationMethod, CalculationType, PowerGridModel, initialize_array, validation
from power_grid_model.utils import json_deserialize, json_serialize_to_file
from power_grid_model.validation import ValidationException, assert_valid_batch_data, assert_valid_input_data

from power_system_simulation.calculation_module import *


def optimal_tap_position():
    pass