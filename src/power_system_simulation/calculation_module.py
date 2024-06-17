"""
Power Grid Calculation Module

This script performs power flow analysis on a given power grid network 
using provided active and reactive power profile data.
It calculates voltage statistics and line loading information based on the power flow results.

Authors: Rick Eversdijk, Luka Nielsen, Carmelo Vella, David van Warmerdam, Codrin Dănculea
Date: 25/05/2024

"""

from typing import Dict

import numpy as np
import pandas as pd
from power_grid_model import CalculationMethod, CalculationType, PowerGridModel, initialize_array, validation
from power_grid_model.utils import json_deserialize
from power_grid_model.validation import ValidationException, assert_valid_batch_data, assert_valid_input_data


class TimestampsDoNotMatchError(Exception):
    """Exception raised when Timestamps of active and reactive power profiles do not match."""


class LoadIdsDoNotMatchError(Exception):
    """Exception raised when Load IDs of active and reactive power profiles do not match."""


def calculate_power_grid(
    input_network_data: Dict, active_power_profile_path: str, reactive_power_profile_path: str
) -> Dict:
    """
    Analyze power flow on the given power grid network using provided active and reactive power profile data.

    Args:
        input_network_data (Dict): Input network data in JSON format.
        active_power_profile_path (str): Path to the parquet file containing active power profile data.
        reactive_power_profile_path (str): Path to the parquet file containing reactive power profile data.

    Returns:
        Dict: Aggregated power flow results containing voltage statistics and line loading information.
    """
    # Load input network data
    with open(input_network_data) as fp:
        input_data = json_deserialize(fp.read())

    # Validate input data
    assert_valid_input_data(input_data=input_data, calculation_type=CalculationType.power_flow)
    model = PowerGridModel(input_data=input_data)

    # Load active and reactive power profiles
    active_power_profile = pd.read_parquet(active_power_profile_path)
    reactive_power_profile = pd.read_parquet(reactive_power_profile_path)

    # Check if timestamps and load IDs match
    if not active_power_profile.index.equals(reactive_power_profile.index):
        raise TimestampsDoNotMatchError("Timestamps of active and reactive power profiles do not match.")
    if not (active_power_profile.columns == reactive_power_profile.columns).all():
        raise LoadIdsDoNotMatchError("Load IDs of active and reactive power profiles do not match.")

    # Create PGM batch update dataset
    load_profile = initialize_array("update", "sym_load", active_power_profile.shape)
    load_profile["id"] = active_power_profile.columns.to_numpy()
    load_profile["p_specified"] = active_power_profile.to_numpy()
    load_profile["q_specified"] = reactive_power_profile.to_numpy()
    update_data = {"sym_load": load_profile}

    # Validate batch data
    assert_valid_batch_data(input_data=input_data, update_data=update_data, calculation_type=CalculationType.power_flow)

    # Run power flow calculations
    output_data = model.calculate_power_flow(
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
