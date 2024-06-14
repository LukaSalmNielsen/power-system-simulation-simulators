import json
import time
import math
import random
from typing import Dict
from IPython.display import display
import pprint
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib as plt
from power_grid_model import CalculationMethod, CalculationType, PowerGridModel, initialize_array
from power_grid_model.utils import json_deserialize, json_serialize
from power_grid_model.validation import assert_valid_batch_data, assert_valid_input_data
from power_system_simulation.graph_processing import GraphProcessor as gp


def EVpenetration(input_network_data: str,
        meta_data_str: str,
        active_power_profile_path: str,
        ev_active_power_profile: str,
        percentage: float,
        seed: int)-> tuple:


    """"""
    with open(input_network_data) as fp:
        input_data = json_deserialize(fp.read(input_network_data))
    assert_valid_input_data(input_data=input_data, calculation_type=CalculationType.power_flow)
    model = PowerGridModel(input_data=input_data)
    with open(meta_data_str, 'r') as file:
        input_metadata = json.load(file)

    active_power_profile = pd.read_parquet(active_power_profile_path)
    ev_power_profile = pd.read_parquet(ev_active_power_profile)

    vertex_ids = input_data['node']['id']
    edge_ids_init = pd.DataFrame(input_data['line']['id']).to_numpy()
    edge_vertex_id_pairs_init = list(zip(input_data['line']['from_node'], input_data['line']['to_node']))
    edge_enabled_init = (input_data['line']['from_status'] == 1) & (input_data['line']['to_status'] == 1)
    source_id = input_data['node'][0][0] # or meta_data

    ########### MODIFIED DATA FOR TRANSFORMER AS EDGE
    vertex_ids = vertex_ids
    edge_ids = np.append(edge_ids_init, input_data['transformer']['id']).tolist()
    edge_vertex_id_pairs = (edge_vertex_id_pairs_init) + [(source_id,input_metadata['lv_busbar'])]
    edge_enabled = np.append(edge_enabled_init,[True])
    source_id = source_id

    ############################
    # call GraphProcessing.py  #
    ############################
    G = gp(vertex_ids = vertex_ids, edge_ids= edge_ids, edge_vertex_id_pairs= edge_vertex_id_pairs, edge_enabled= edge_enabled, source_vertex_id= source_id)
    model = PowerGridModel(input_data)
    # Set the random seed for reproducibility
    random.seed(seed)
    
    # Get the number of feeders
    no_feeders = len(input_metadata.get('lv_feeders', []))
    print(f'The number of feeders in the lv_feeders array is: {no_feeders}')
    
    # Get the number of sym_load entries
    no_house = len(input_data['sym_load'])
    print(f'The number of sym_load entries is: {no_house}')
    
    # Calculate EV_feeder using math.floor to round down
    EV_feeder = math.floor((percentage / 100) * no_house / no_feeders)
    print(f'The number of EVs per feeder is: {EV_feeder}')
    
    # Print all sym_load node IDs and corresponding IDs
    print("Sym_load IDs and their nodes:")
    for i in range(no_house):
        print(f"ID: {input_data['sym_load'][i]['id']}, Node: {input_data['sym_load'][i]['node']}")
    
    # Dictionary to store which sym_load belongs to which feeder
    feeder_to_loads = {feeder: [] for feeder in input_metadata['lv_feeders']}
    selected_ids = []
    # Iterate through each feeder and call the function gp.find_downstream_vertices
    for feeder in input_metadata['lv_feeders']:
        print(f'Processing feeder: {feeder}')
        downstream_vertices = G.find_downstream_vertices(feeder)
        print(f'Downstream vertices for {feeder}: {downstream_vertices}')
        
        # Check if sym_load node ids are found within the returned list
        matched_loads = [load['id'] for load in input_data['sym_load'] if load['node'] in downstream_vertices]
        
        # Randomly select EV_feeder number of IDs from the matched loads
        if len(matched_loads) > 0:
            selected_ids_for_feeder = random.sample(matched_loads, min(EV_feeder, len(matched_loads)))
            feeder_to_loads[feeder].extend(selected_ids_for_feeder)
            selected_ids.extend(selected_ids_for_feeder)
    
    filtered_profile = active_power_profile[selected_ids]
    print("Filtered active_power_profile DataFrame:")
    print(filtered_profile)
    
    # Print the mapping of feeders to loads
    for feeder, loads in feeder_to_loads.items():
        print(f'Feeder {feeder} has selected loads: {loads}')
    
    # Randomly select an equal number of columns from ev_power_profile
    num_selected = len(selected_ids)
    selected_columns = random.sample(ev_power_profile.columns.tolist(), num_selected)
    selected_ev_profile = ev_power_profile[selected_columns]
    
    # Ensure the indexes and columns are aligned properly
    selected_ev_profile.index = filtered_profile.index
    selected_ev_profile.columns = filtered_profile.columns
    
    # Perform element-wise addition of the filtered profiles
    summed_profile = filtered_profile.add(selected_ev_profile, fill_value=0)
    
    print("Summed Profile DataFrame:")
    print(summed_profile)
    
    update_sym_load = initialize_array("update", "sym_load", summed_profile.shape)
    update_sym_load['id'] = summed_profile.columns.to_numpy()
    update_sym_load['p_specified'] = summed_profile.to_numpy()


    update_data = {"sym_load": update_sym_load}

    from power_grid_model.validation import assert_valid_batch_data
    assert_valid_batch_data(input_data=input_data, update_data=update_data, calculation_type=CalculationType.power_flow) 

    model_2 = model.copy()
    model_2.update(update_data=update_data)     

    output_data = model_2.calculate_power_flow(
        update_data=update_data, calculation_method=CalculationMethod.newton_raphson
    )

    # Extract necessary data from output_data
    node_voltages = output_data["node"]["u_pu"]
    node_ids = output_data["node"]["id"]
    line_loadings = output_data["line"]["loading"]
    line_ids = output_data["line"]["id"]
    p_from = output_data["line"]["p_from"]
    p_to = output_data["line"]["p_to"]
    timestamps = active_power_profile.index

    # Aggregating voltage results
    voltage_results = []
    for i, timestamp in enumerate(timestamps):
        max_voltage = node_voltages[i].max()
        min_voltage = node_voltages[i].min()
        max_voltage_node = node_ids[i, np.argmax(node_voltages[i])]
        min_voltage_node = node_ids[i, np.argmin(node_voltages[i])]

        voltage_results.append(
            {
                "Timestamp": timestamp,
                "Max_Voltage": max_voltage,
                "Max_Voltage_Node": max_voltage_node,
                "Min_Voltage": min_voltage,
                "Min_Voltage_Node": min_voltage_node,
            }
        )

    # Aggregating line loading results
    line_results = []
    count = 0
    for line_id in np.unique(line_ids):
        loadings = line_loadings[line_ids == line_id]
        max_loading = loadings.max()
        min_loading = loadings.min()
        max_loading_time = timestamps[loadings.argmax()]
        min_loading_time = timestamps[loadings.argmin()]
        energy_losses = abs(p_from[:, count] + p_to[:, count])
        energy_loss_kwh = np.trapz(energy_losses) / 1000
        count = count + 1

        line_results.append(
            {
                "Line_ID": line_id,
                "Total_Loss": energy_loss_kwh,
                "Max_Loading": max_loading,
                "Max_Loading_Timestamp": max_loading_time,
                "Min_Loading": min_loading,
                "Min_Loading_Timestamp": min_loading_time,
            }
        )

    # Create DataFrame for voltage results
    voltage_df = pd.DataFrame(voltage_results)
    voltage_df.set_index("Timestamp", inplace=True)

    # Create DataFrame for line results
    line_df = pd.DataFrame(line_results)
    line_df.set_index("Line_ID", inplace=True)

    # Return aggregated results
    return voltage_df, line_df

EVpenetration(50, 41)