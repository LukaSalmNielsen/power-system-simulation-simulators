import pandas as pd
import pytest

from power_system_simulation.optimal_tap_position import *

# Input data
input_network_data = "src/data/input/input_network_data.json"
active_power_profile_path = "src/data/input/active_power_profile.parquet"
reactive_power_profile_path = "src/data/input/reactive_power_profile.parquet"


# Test output for minimal total energy loss of all the lines and the whole time period.
def test_optimal_tap_position_total_losses_min():
    tap_position_total_losses = optimal_tap_position(
        input_network_data, active_power_profile_path, reactive_power_profile_path, 0
    )
    pd.testing.assert_frame_equal(tap_position_total_losses, 5)


# Test output for minimal (averaged across all nodes) deviation of (max and min) p.u. node voltages with respect to 1 p.u.
def test_optimal_tap_position_average_dev_min():
    tap_position_average_dev = optimal_tap_position(
        input_network_data, active_power_profile_path, reactive_power_profile_path, 1
    )
    pd.testing.assert_frame_equal(tap_position_average_dev, 3)


# Test if function raises exception if invalid optimize input is given
def test_InvalidOptimizeInput():
    with pytest.raises(InvalidOptimizeInput):
        tap_position = optimal_tap_position(
            input_network_data, active_power_profile_path, reactive_power_profile_path, 5
        )
