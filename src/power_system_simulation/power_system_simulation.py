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


class power_system_simulation:
    """_summary_
    class that processes the data
    """

    def __init__(
        input_network_data: Dict, meta_data: Dict, active_power_profile_path: str, reactive_power_profile_path: str
    ) -> Dict:
        """
        Check the following validity criteria for the input data. Raise or passthrough relevant errors.
            * The LV grid should be a valid PGM input data.
            * The LV grid has exactly one transformer, and one source.
            * All IDs in the LV Feeder IDs are valid line IDs.
            * All the lines in the LV Feeder IDs have the from_node the same as the to_node of the transformer.
            * The grid is fully connected in the initial state.
            * The grid has no cycles in the initial state.
            * The timestamps are matching between the active load profile, reactive load profile, and EV charging profile.
            * The IDs in active load profile and reactive load profile are matching.
            * The IDs in active load profile and reactive load profile are valid IDs of sym_load.
            * The number of EV charging profile is at least the same as the number of sym_load.
        """
        # Load meta data and check 1 source and 1 transformer
        with open(meta_data) as fp:
            meta_data = json_deserialize(fp.read())

        if len(meta_data['source']) != 1:
            raise

        if len(meta_data['transformer']) != 1:
            raise

        # Do power flow calculations with validity checks
        voltage_results, line_results = calculate_power_grid(
                input_network_data, active_power_profile_path, reactive_power_profile_path
            )
        
        