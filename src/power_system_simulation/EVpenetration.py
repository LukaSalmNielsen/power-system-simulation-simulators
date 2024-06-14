import json
import math
import pprint
import time
from typing import Dict

import matplotlib as plt
import networkx as nx
import numpy as np
import pandas as pd
from IPython.display import display
from power_grid_model import CalculationMethod, CalculationType, PowerGridModel, initialize_array
from power_grid_model.utils import json_deserialize, json_serialize
from power_grid_model.validation import assert_valid_batch_data, assert_valid_input_data

from power_system_simulation.graph_processing import GraphProcessor as gp

with open("C:/Users/20221688/Desktop/small_network/input/input_network_data.json") as fp:
    input_data = json_deserialize(fp.read())
assert_valid_input_data(input_data=input_data, calculation_type=CalculationType.power_flow)
model = PowerGridModel(input_data=input_data)
with open("C:/Users/20221688/Desktop/small_network/input/meta_data.json", "r") as file:
    input_metadata = json.load(file)

active_power_profile = pd.read_parquet("C:/Users/20221688/Desktop/small_network/input/active_power_profile.parquet")
reactive_power_profile = pd.read_parquet("C:/Users/20221688/Desktop/small_network/input/reactive_power_profile.parquet")
ev_power_profile = pd.read_parquet("C:/Users/20221688/Desktop/small_network/input/ev_active_power_profile.parquet")

######ORIGINAL DATA
##pprint.pprint(input_data)
vertex_ids = input_data["node"]["id"]
edge_ids_init = pd.DataFrame(input_data["line"]["id"]).to_numpy()
edge_vertex_id_pairs_init = list(zip(input_data["line"]["from_node"], input_data["line"]["to_node"]))
edge_enabled_init = (input_data["line"]["from_status"] == 1) & (input_data["line"]["to_status"] == 1)
source_id = input_data["node"][0][0]  # or meta_data

########### MODIFIED DATA FOR TRANSFORMER AS EDGE
vertex_ids = vertex_ids
edge_ids = np.append(edge_ids_init, input_data["transformer"]["id"]).tolist()
edge_vertex_id_pairs = (edge_vertex_id_pairs_init) + [(source_id, input_metadata["lv_busbar"])]
edge_enabled = np.append(edge_enabled_init, [True])
source_id = source_id

############################
# call GraphProcessing.py  #
############################
G = gp(
    vertex_ids=vertex_ids,
    edge_ids=edge_ids,
    edge_vertex_id_pairs=edge_vertex_id_pairs,
    edge_enabled=edge_enabled,
    source_vertex_id=source_id,
)

nx.draw(G.graph, with_labels=True)
pprint.pprint(active_power_profile)


# fourhundred = ev_power_profile
# print(fourhundred)
def EVpenetration(percentage: float) -> int:
    # Get the number of feeders

    no_feeders = len(input_metadata.get("lv_feeders", []))
    print(f"The number of feeders in the lv_feeders array is: {no_feeders}")

    # Get the number of sym_load entries
    no_house = len(input_data["sym_load"])
    print(f"The number of sym_load entries is: {no_house}")

    EV_feeder = math.floor((percentage / 100) * no_house / no_feeders)
    print(f"The number of EVs per feeder is: {EV_feeder}")

    # Print all sym_load node IDs and corresponding IDs
    print("Sym_load IDs and their nodes:")
    for i in range(no_house):
        print(f"ID: {input_data['sym_load']['id'][i]}, Node: {input_data['sym_load']['node'][i]}")

    # Dictionary to store which sym_load belongs to which feeder
    feeder_to_loads = {feeder: [] for feeder in input_metadata["lv_feeders"]}

    # Iterate through each feeder and call the function gp.find_downstream_vertices
    for feeder in input_metadata["lv_feeders"]:
        print(f"Processing feeder: {feeder}")
        downstream_vertices = G.find_downstream_vertices(feeder)
        print(f"Downstream vertices for {feeder}: {downstream_vertices}")

        # Check if sym_load node ids are found within the returned list
        for load in input_data["sym_load"]:
            if load["node"] in downstream_vertices:
                feeder_to_loads[feeder].append(load["id"])

    # Print the mapping of feeders to loads
    for feeder, loads in feeder_to_loads.items():
        print(f"Feeder {feeder} has loads: {loads}")

    return no_feeders  # Example return value


EVpenetration(50)
