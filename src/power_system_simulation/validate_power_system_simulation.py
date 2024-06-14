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

from . import calculation_module as calc, graph_processing as graph


class TooManyTransformers(Exception):
    """The Transformer entry either is more than one or has an incorrect format"""


class TooManySources(Exception):
    """The Source entry either is more than one or has an incorrect format"""


class NotAllFeederIDsareValid(Exception):
    """The feeder IDs do not match the ids in the Network data"""


class TransformerAndFeedersNotConnected(Exception):
    """The transformer is not connected to the same node from which the feeders are connected"""

class TooFewEVs(Exception):
    """There are less EVs than Symloads, ensure that they are at least equal"""


class validate_power_system_simulation:
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
        # Read and load input data
    
        ev_power_profile = pd.read_parquet(ev_active_power_profile)

        with open(meta_data_str, "r") as fp:
            meta_data = json.load(fp)

        with open(input_network_data, "r") as fp:
            input_data = json_deserialize(fp.read())

        #ensure that there is only ever one Source
        if type(meta_data["source"]) != int:
            raise TooManySources("This Input data contains more than one source")

        #ensure that there is only ever one Transformer
        if type(meta_data["transformer"]) != int:
            raise TooManyTransformers("This Input data contains more than one transformer")

        #filter the line ids and feeders
        line_ids = input_data["line"]["id"]
        feeder_ids = meta_data["lv_feeders"]

        #Compare the contents of the feeders and line ids to ensure that they match, throw an exception if they don't
        if not np.all(np.isin(feeder_ids, line_ids)):
            raise NotAllFeederIDsareValid("not all feeders are valid lines")

        #Filter the Symloads and count them, do the same for the number of EV-profiles 
        no_house = len(input_data['sym_load'])
        a = np.matrix(ev_power_profile)

        #Compare the number of EV-profiles to the Number of symloads, if the number of symloads is more than the amount of EVs then throw an exception
        if not a.shape[1] >= no_house: 
            raise TooFewEVs("not enough EV_profiles")
        
        #Filter the matrix in order to find the number of transformers vs the number of feeders and then compare their to and from nodes
        line_ids = input_data["line"]["id"]
        feeder_ids = meta_data["lv_feeders"]
        line_Matrix = np.column_stack((input_data["line"]["id"], input_data["line"]["from_node"]))
        mask = np.isin(line_Matrix[:, 0], feeder_ids)
        filtered_matrix = line_Matrix[mask]
        transformer = input_data["transformer"]["to_node"]

        #compare the to nodes of the transformer to the from nodes from the feeders and throw an exception if it doesn't allign
        for i in filtered_matrix:
            if i[1] != transformer:
                raise TransformerAndFeedersNotConnected("not all feeders are connected to the transformer")

        # validate data for PGM
        assert_valid_input_data(input_data=input_data, calculation_type=CalculationType.power_flow)

        ##########The graphprocessor can now be called to check that no exceptions are called##########
        ######ORIGINAL DATA
        ##pprint.pprint(input_data)
        vertex_ids = input_data['node']['id']
        edge_ids_init = pd.DataFrame(input_data['line']['id']).to_numpy()
        edge_vertex_id_pairs_init = list(zip(input_data['line']['from_node'], input_data['line']['to_node']))
        edge_enabled_init = (input_data['line']['from_status'] == 1) & (input_data['line']['to_status'] == 1)
        source_id = input_data['node'][0][0] # or meta_data

        ########### MODIFIED DATA FOR TRANSFORMER AS EDGE
        vertex_ids = vertex_ids
        edge_ids = np.append(edge_ids_init, input_data['transformer']['id']).tolist()
        edge_vertex_id_pairs = (edge_vertex_id_pairs_init) + [(source_id,meta_data['lv_busbar'])]
        edge_enabled = np.append(edge_enabled_init,[True])
        source_id = source_id

        ############################
        # call GraphProcessing.py  #
        ############################
        graph.GraphProcessor(vertex_ids,edge_ids,edge_vertex_id_pairs,edge_enabled,source_id)       


        ##########Now the calculation module is called to see if any exceptions are called.##########
        ############################
        # call calculation_module.py  #
        ############################
        voltage_results, line_results = calc.calculate_power_grid(
            input_network_data, active_power_profile_path, reactive_power_profile_path
        )
