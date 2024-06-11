import pandas as pd
import pytest
from power_grid_model import CalculationMethod, CalculationType, PowerGridModel, initialize_array, validation
from power_grid_model.utils import json_deserialize, json_serialize_to_file
from power_grid_model.validation import ValidationException, assert_valid_batch_data, assert_valid_input_data

from power_system_simulation.calculation_module import (
    LoadIdsDoNotMatchError,
    TimestampsDoNotMatchError,
    calculate_power_grid,
)

# Input data
input_network_data = "src\\data\\Calculation_module_test\\input\\input_network_data.json"
active_power_profile_path = "src\\data\\Calculation_module_test\\input\\active_power_profile.parquet"
reactive_power_profile_path = "src\\data\\Calculation_module_test\\input\\reactive_power_profile.parquet"

# Incorrect input data
modified_timestamp_active_power_profile_path = (
    "src\\data\\Calculation_module_test\\modified_timestamp_active_power_profile.parquet"
)
modified_id_reactive_power_profile_path = (
    "src\\data\\Calculation_module_test\\modified_id_reactive_power_profile.parquet"
)
modified_load_reactive_power_profile_path = (
    "src\\data\\Calculation_module_test\\modified_load_reactive_power_profile.parquet"
)
incorrect_network = "src\\data\\Calculation_module_test\\input\\incorrect_network.json"

# Make incorrect timestamp
active_power_profile = pd.read_parquet(active_power_profile_path)
original_timestamp = active_power_profile.index[0]
new_timestamp = pd.Timestamp("1234-01-01 00:00:00")
active_power_profile.index = active_power_profile.index.map(
    lambda ts: new_timestamp if ts == original_timestamp else ts
)
active_power_profile.to_parquet(modified_timestamp_active_power_profile_path)

# Make incorrect ID
reactive_power_profile = pd.read_parquet(reactive_power_profile_path)
reactive_power_profile.rename(columns={8: 99999}, inplace=True)
reactive_power_profile.to_parquet(modified_id_reactive_power_profile_path)

# Change load
reactive_power_profile = pd.read_parquet(reactive_power_profile_path)
reactive_power_profile.iloc[0, 0] = 99999
reactive_power_profile.to_parquet(modified_load_reactive_power_profile_path)

# Correct output data
check_table_voltage = pd.read_parquet(
    "src\\data\Calculation_module_test\\expected_output\\output_table_row_per_timestamp.parquet"
)
check_table_line = pd.read_parquet(
    "src\\data\\Calculation_module_test\\expected_output\\output_table_row_per_line.parquet"
)

# Make invalid network
node_error = initialize_array("input", "node", 3)
node_error["id"] = [1, 2, 3]
node_error["u_rated"] = [10.5e3]

line_error = initialize_array("input", "line", 3)
line_error["id"] = [4, 5, 6]
line_error["from_node"] = [1, 2, 3]
line_error["to_node"] = [2, 3, 4]
line_error["from_status"] = [True]
line_error["to_status"] = [True]
line_error["r1"] = [0.25]
line_error["x1"] = [0.2]
line_error["c1"] = [10e-6]
line_error["tan1"] = [0.0]

sensor_error = initialize_array("input", "sym_power_sensor", 2)
sensor_error["id"] = [6, 7]
sensor_error["measured_object"] = [3, 4]
sensor_error["measured_terminal_type"] = [0, 2]
sensor_error["p_measured"] = [0]
sensor_error["q_measured"] = [0]
sensor_error["power_sigma"] = [0]

error_data = {"node": node_error, "line": line_error, "sym_power_sensor": sensor_error}
json_serialize_to_file(incorrect_network, error_data)


def test_TimestampsDoNotMatchError():
    with pytest.raises(TimestampsDoNotMatchError):
        voltage_results, line_results = calculate_power_grid(
            input_network_data, modified_timestamp_active_power_profile_path, reactive_power_profile_path
        )


def test_LoadIdsDoNotMatchError():
    with pytest.raises(LoadIdsDoNotMatchError):
        voltage_results, line_results = calculate_power_grid(
            input_network_data, active_power_profile_path, modified_id_reactive_power_profile_path
        )


# Output should match the correct output
def test_calculate_power_grid():
    voltage_results, line_results = calculate_power_grid(
        input_network_data, active_power_profile_path, reactive_power_profile_path
    )
    pd.testing.assert_frame_equal(voltage_results, check_table_voltage)
    pd.testing.assert_frame_equal(line_results, check_table_line)


# Output should not match the correct output due to changed load
def test2_calculate_power_grid():
    voltage_results, line_results = calculate_power_grid(
        input_network_data, active_power_profile_path, modified_load_reactive_power_profile_path
    )
    with pytest.raises(AssertionError):
        pd.testing.assert_frame_equal(voltage_results, check_table_voltage)
    with pytest.raises(AssertionError):
        pd.testing.assert_frame_equal(line_results, check_table_line)


# Ensure that the ValidationException is raised when invalid data is provided
def test_ValidationException():
    with pytest.raises(ValidationException):
        calculate_power_grid(incorrect_network, active_power_profile_path, reactive_power_profile_path)
