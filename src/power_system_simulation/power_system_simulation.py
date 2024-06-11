# Load dependencies and functions from graph_processing
import copy
import json
from typing import Dict, List, Tuple

import networkx as nx
import numpy as np

# Load dependencies and functions from calculation_module
import pandas as pd
from power_grid_model import CalculationMethod, CalculationType, PowerGridModel, initialize_array, validation
from power_grid_model.utils import json_deserialize, json_serialize_to_file
from power_grid_model.validation import ValidationException, assert_valid_batch_data, assert_valid_input_data

from . import calculation_module as calc
from . import graph_processing as graph


class TooManyTransformers(Exception):
    """Done"""


class TooManySources(Exception):
    """Done"""


class NotAllFeederIDsareValid(Exception):
    """Done"""


class TransformerAndFeedersNotConnected(Exception):
    """working on it"""


class TheIDsAreNotValid(Exception):
    """empty for now"""


class TooFewEVs(Exception):
    """empty for now"""


class power_system_simulation:
    """_summary_
    (input_network_data: str), (meta_data: str), (active_power_profile_path: str), (reactive_power_profile_path: str), (ev_active_power_profile: str)
    Checks and validates all of the data for this package.
    """

    def __init__(
            self,
        input_network_data: str,
        meta_data_str: str,
        active_power_profile_path: str,
        reactive_power_profile_path: str,
        ev_active_power_profile: str,
    ) -> Dict:
        """
        Check the following validity criteria for the input data. Raise or passthrough relevant errors.
            * The LV grid should be a valid PGM input data. (This should already be checked in the calculation_module but just in case ill check here as well)
            * The LV grid has exactly one transformer, and one source. (Done)
            * All IDs in the LV Feeder IDs are valid line IDs. (Done)
            * All the lines in the LV Feeder IDs have the from_node the same as the to_node of the transformer.
            * The grid is fully connected in the initial state. (Done by calling graphprocessort)
            * The grid has no cycles in the initial state.(Done by calling graphprocessort)
            * The timestamps are matching between the active load profile, reactive load profile, and EV charging profile. (unsure, this might just be checkable in the calculation_module)
            * The IDs in active load profile and reactive load profile are matching. (Done by Rick)
            * The IDs in active load profile and reactive load profile are valid IDs of sym_load. (Done by Rick)
            * The number of EV charging profile is at least the same as the number of sym_load. (this should also be checked there in calculation module I think)
        """
        # Do power flow calculations with validity checks
        # Load meta data and check 1 source and 1 transformer

        with open(meta_data_str, "r") as fp:
            meta_data = json.load(fp)

        if type(meta_data["source"]) != int:
            raise TooManySources("This Input data contains more than one source")

        if type(meta_data["transformer"]) != int:
            raise TooManyTransformers("This Input data contains more than one transformer")

        # read input data
        with open(input_network_data, "r") as fp:
            input_data = json_deserialize(fp.read())

        line_ids = input_data["line"]["id"]
        feeder_ids = meta_data["lv_feeders"]

        if not np.all(np.isin(feeder_ids, line_ids)):
            raise NotAllFeederIDsareValid("not all feeders are valid lines")

        line_ids = input_data["line"]["id"]
        print(line_ids)
        feeder_ids = meta_data["lv_feeders"]
        print(feeder_ids)
        line_Matrix = np.column_stack((input_data["line"]["id"], input_data["line"]["from_node"]))
        print(line_Matrix)
        mask = np.isin(line_Matrix[:, 0], feeder_ids)
        filtered_matrix = line_Matrix[mask]
        print(filtered_matrix)
        transformer = input_data["transformer"]["to_node"]
        print(transformer)

        for i in filtered_matrix:
            if i[1] != transformer:
                raise TransformerAndFeedersNotConnected("not all feeders are connected to the transformer")

        # validate data for PGM
        assert_valid_input_data(input_data=input_data, calculation_type=CalculationType.power_flow)

        # The graphprocessor can now be called

        # calculate_power_grid(
        #    input_network_data, active_power_profile_path, reactive_power_profile_path
        # )
