from pathlib import Path

import pytest

import power_system_simulation.nm_calculation as nm_file

######################################################################
# Data path handling (used for calling the class Nm1_calculation.py) #
######################################################################

DATA_PATH = Path(__file__).parent / "data"
DATA_EXCEPTION_SET = DATA_PATH / "Exception_test_data"
metadata_path = DATA_EXCEPTION_SET / "meta_data.json"
input_network_path = DATA_EXCEPTION_SET / "input_network_data.json"
active_power_profile_path = DATA_EXCEPTION_SET / "active_power_profile.parquet"
reactive_power_profile_path = DATA_EXCEPTION_SET / "reactive_power_profile.parquet"


def test_nm_scenario_class():
    assert nm_file.nm_function(
        18, input_network_path, metadata_path, active_power_profile_path, reactive_power_profile_path
    ) == [24]
