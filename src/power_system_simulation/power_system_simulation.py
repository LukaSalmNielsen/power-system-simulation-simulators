# Load dependencies and functions from graph_processing
import copy
from typing import List, Tuple

import networkx as nx

# Load dependencies and functions from calculation_module
import pandas as pd
from power_grid_model import CalculationMethod, CalculationType, PowerGridModel, initialize_array, validation
from power_grid_model.utils import json_deserialize, json_serialize_to_file
from power_grid_model.validation import ValidationException, assert_valid_batch_data, assert_valid_input_data

from src.power_system_simulation.calculation_module import *
from src.power_system_simulation.graph_processing import *

class TooManyTransformers(Exception):
    """empty for now"""


class TooManySources(Exception):
    """empty for now"""


class NotAllFeederIDsareValid(Exception):
    """empty for now"""


class TheGridIsNotConnected(Exception):
    """empty for now"""


class TheGridHasCycles(Exception):
    """empty for now"""


class TheTimestampsDontMatch(Exception):
    """empty for now"""


class TheIDsDontMatch(Exception):
    """empty for now"""


class TheIDsAreNotValid(Exception):
    """empty for now"""


class TooFewEVs(Exception):
    """empty for now"""

class power_system_simulation:
    print("hallo")
    """_summary_
    class that processes the data
    """
    def __init__(
        input_network_data: str, meta_data: str, active_power_profile_path: str, reactive_power_profile_path: str, ev_active_power_profile: str, 
    ) -> Dict:
        """
        Check the following validity criteria for the input data. Raise or passthrough relevant errors.
            * The LV grid should be a valid PGM input data. (This should already be checked in the calculation_module but just in case ill check here as well)
            * The LV grid has exactly one transformer, and one source. (David made code that makes quite a bit of sense, just added the raises correctly)
            * All IDs in the LV Feeder IDs are valid line IDs.
            * All the lines in the LV Feeder IDs have the from_node the same as the to_node of the transformer.
            * The grid is fully connected in the initial state.
            * The grid has no cycles in the initial state.
            * The timestamps are matching between the active load profile, reactive load profile, and EV charging profile.
            * The IDs in active load profile and reactive load profile are matching.
            * The IDs in active load profile and reactive load profile are valid IDs of sym_load.
            * The number of EV charging profile is at least the same as the number of sym_load.
        """
        # Do power flow calculations with validity checks
        # Load meta data and check 1 source and 1 transformer
        with open(meta_data) as fp:
            meta_data = json_deserialize(fp.read())

        if len(meta_data["source"]) != 1:
            raise TooManySources("This Input data contains more than one source")

        if len(meta_data["transformer"]) != 1:
            raise TooManyTransformers("This Input data contains more than one transformer")

        #read input data
        with open(input_network_data) as fp:
            input_data = json_deserialize(fp.read())
        
        #validate data for PGM
        assert_valid_input_data(input_data=input_data, calculation_type=CalculationType.power_flow)

        for i in meta_data["lv_feeders"]:
            if i not in input_data["line","id"]:
                raise NotAllFeederIDsareValid("not all feeders corrospond to a line")

        voltage_results, line_results = calculate_power_grid(
            input_network_data, active_power_profile_path, reactive_power_profile_path
        )

power_system_simulation("meta_data.json")