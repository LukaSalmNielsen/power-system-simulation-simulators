"""module responsible for calculating the N-1 Scenarios"""

##################
# IMPORT MODULES #
##################

import copy
import json
import time
from datetime import datetime, timedelta


import numpy as np
import pandas as pd

from power_grid_model import CalculationMethod, CalculationType, PowerGridModel, initialize_array
from power_grid_model.utils import json_deserialize
from power_grid_model.validation import assert_valid_input_data
from prettytable import PrettyTable

from power_system_simulation.graph_processing import GraphProcessor as gp

class IDNotFoundError(Exception):
    """The inserted line ID is not valid"""


class lineIDnotConnectedOnBothSides(Exception):
    """The insterted line ID is not connected at both sides"""



################################################
# TIME CLASS for tracking time in calculations #
################################################


class Timer:
    """TIME CLASS for tracking time in calculations"""
    def __init__(self, name: str):
        self.name = name
        self.start = None

    def __enter__(self):
        self.start = time.perf_counter()

    def __exit__(self, *args):
        print(f"Execution time for {self.name} is {(time.perf_counter() - self.start):0.6f} s")


def nm_function(
    given_lineid: int,
    input_data_path: str,
    metadata_path: str,
    active_power_profile_path: str,
    reactive_power_profile_path: str,
) -> list[int]:
    """module responsible for calculating the N-1 Scenarios"""
    #################################
    # Open data from provided paths #
    #################################

    with open(metadata_path, "r", encoding="utf-8") as fp:
        meta_data = json.load(fp)

    with open(input_data_path, "r", encoding="utf-8") as fp:
        input_data = json_deserialize(fp.read())

    assert_valid_input_data(input_data=input_data, calculation_type=CalculationType.power_flow)

    active_power_profile = pd.read_parquet(active_power_profile_path)
    reactive_power_profile = pd.read_parquet(reactive_power_profile_path)

    ##############################################
    # extract input data for graph from original #
    ##############################################

    ########### ORIGINAL DATA is extracted for "graph_processing.py" call
    vertex_ids = input_data["node"]["id"]
    edge_ids_init = pd.DataFrame(input_data["line"]["id"]).to_numpy()
    edge_vertex_id_pairs_init = list(zip(input_data["line"]["from_node"], input_data["line"]["to_node"]))
    edge_enabled_init = (input_data["line"]["from_status"] == 1) & (input_data["line"]["to_status"] == 1)
    source_id = input_data["node"][0][0]  # or meta_data

    ########### MODIFIED DATA FOR TRANSFORMER AS EDGE

    # Transformer must be added as edge -> add one more edge_vertex_id_pair: (0,1)
    # one more edge enabled (True) and one more edge id (tranformer id).
    # They can all be appended at the end of the list(s)
    edge_ids = np.append(edge_ids_init, input_data["transformer"]["id"])
    edge_vertex_id_pairs = (edge_vertex_id_pairs_init) + [(source_id, meta_data["lv_busbar"])]
    edge_enabled = np.append(edge_enabled_init, [True])

    ############################
    # call GraphProcessing.py  #
    ############################
    gra = gp(
        vertex_ids=vertex_ids,
        edge_ids=edge_ids,
        edge_vertex_id_pairs=edge_vertex_id_pairs,
        edge_enabled=edge_enabled,
        source_vertex_id=source_id,
    )

    ################
    #    ERRORS    #
    ################

    # ERROR 1: ID NOT VALID
    if not isinstance(given_lineid, int):
        raise IDNotFoundError("The inserted line ID is not valid")

    # ERROR 2: ID NOT CONNECTED AT BOTH SIDES
    if (
        input_data["line"]["from_status"][input_data["line"]["id"] == given_lineid] == 0
        or input_data["line"]["to_status"][input_data["line"]["id"] == given_lineid] == 0
    ):
        raise lineIDnotConnectedOnBothSides("The insterted line ID is not connected at both sides")

    #####################
    #    CALCULATION    #
    #####################

    # find alternative edge(s) for "given_lineID"
    alt_list = gra.find_alternative_edges(given_lineid)

    # PREPARE OUTPUT TABLE
    table = PrettyTable(["Alternative ID", "Max Loading", "ID_max", "Timestamp_max"])

    # for every alt edge create a copy of the input data and perform load profile

    for x in alt_list:
        # create the copy of the input data
        new_data = copy.copy(input_data)
        # turn on edge with ID=x and turn off edge with given_edgeID for the new_data
        new_data["line"]["to_status"][new_data["line"]["id"] == x] = [1]
        new_data["line"]["to_status"][new_data["line"]["id"] == given_lineid] = [0]
        new_data["line"]["from_status"][new_data["line"]["id"] == given_lineid] = [0]
        model = PowerGridModel(input_data=new_data)
        # do the time series power flow
        load_profile = initialize_array("update", "sym_load", (active_power_profile.shape))
        load_profile["id"] = active_power_profile.columns.to_numpy()
        load_profile["p_specified"] = active_power_profile.to_numpy()
        load_profile["q_specified"] = reactive_power_profile.to_numpy()

        update_data = {"sym_load": load_profile}

        with Timer("Batch Calculation using the linear method"):
            output_data = model.calculate_power_flow(
                update_data=update_data, calculation_method=CalculationMethod.linear
            )
        ######### OUTPUT TABLE
        max_line_load = np.amax(output_data["line"]["loading"])
        max_line_load_id = output_data["line"]["id"][output_data["line"]["loading"] == max_line_load][0]
        timestamp_index = np.where(output_data["line"]["loading"] == max_line_load)[0][
            0
        ]  # this returns a number from 0 to 959
        number_of_scenarios = np.where(output_data["line"]["loading"])[0][-1] + 1
        date_list = [datetime(2024, 1, 1) + timedelta(minutes=i * 15) for i in range(number_of_scenarios)]
        table.add_row([x, max_line_load, max_line_load_id, date_list[timestamp_index]])
        ### Delete copies made for current iteration
        del new_data
        del output_data
        del model
        print(table)

    return alt_list
