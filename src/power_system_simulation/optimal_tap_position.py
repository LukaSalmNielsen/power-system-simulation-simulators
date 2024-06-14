""" This module calculated the optimal transformer tap position 
    This is based on input data and the metric of what the user wants it to be optimized by.

Raises:
    InvalidOptimizeInput: raises exception for invalid user input

Returns:
    optimal tap position of the transformer for either minimum total losses (0) or minimum voltage deviation (1)
"""

import numpy as np
from power_grid_model.utils import json_deserialize, json_serialize_to_file

# Load dependencies and functions from calculation_module
from . import calculation_module as calc


class InvalidOptimizeInput(Exception):
    """Expectation raised when user inputs invalid optimize_by value"""


def optimal_tap_position(
    input_network_data: str, active_power_profile_path: str, reactive_power_profile_path: str, optimize_by
):
    """summary

    Args:
        input_network_data
        active_power_profile_path
        reactive_power_profile_path
        optimize_by: based on if user wants optimal tab position based on losses (0) or voltage deviation (1)

    Raises:
        InvalidOptimizeInput: if user does not input 0 or 1 for what to optimize on

    Returns:
        optimal tap position based on what user wants (0 or 1)
    """
    if optimize_by not in (0, 1):
        raise InvalidOptimizeInput("Option to optimize by is invalid, please only input 0 or 1.")

    with open(input_network_data) as fp:
        input_data = json_deserialize(fp.read())

    # Determine min and max tap position
    pos_min = np.take(input_data["transformer"]["tap_min"], 0)
    pos_max = np.take(input_data["transformer"]["tap_max"], 0)
    pos_cur = np.take(input_data["transformer"]["tap_pos"], 0)

    print(pos_min, pos_max)

    # Cycle through all tap positions and change the current tap position
    for tap_pos in range(pos_max, pos_min + 1):
        input_data["transformer"]["tap_pos"] = tap_pos

        # Make sure tap position is changed in the file
        json_serialize_to_file(input_network_data, input_data)

        # run the power calculations
        voltage_results, line_results = calc.calculate_power_grid(
            input_network_data, active_power_profile_path, reactive_power_profile_path
        )

        # get deviation of max node voltage
        average_dev_max_node = ((voltage_results["Max_Voltage_Node"] - 1).abs()).mean()

        # If its the first iteration, set value as min
        if tap_pos == pos_max:
            total_losses_min = (line_results["Total_Loss"]).sum()
            total_losses_min_tap_pos = tap_pos
            average_dev_max_node_min = average_dev_max_node
            average_dev_min_tap_pos = tap_pos
        # Check if new value is lower then already set min value
        else:
            if total_losses_min > (line_results["Total_Loss"]).sum():
                total_losses_min = (line_results["Total_Loss"]).sum()
                total_losses_min_tap_pos = tap_pos
            if average_dev_max_node_min > average_dev_max_node:
                average_dev_max_node_min = average_dev_max_node
                average_dev_min_tap_pos = tap_pos

    # Set file back to original tap position
    input_data["transformer"]["tap_pos"] = pos_cur
    json_serialize_to_file(input_network_data, input_data)

    if optimize_by == 0:
        return total_losses_min_tap_pos
    if optimize_by == 1:
        return average_dev_min_tap_pos
    return
