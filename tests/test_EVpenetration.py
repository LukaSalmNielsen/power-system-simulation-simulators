from pathlib import Path

import pytest

import power_system_simulation.ev_penetration as EV

DATA_PATH = Path(__file__).parent / "data"
DATA_EXCEPTION_SET = DATA_PATH / "Exception_test_data"


# correct input data
metadata = DATA_EXCEPTION_SET / "meta_data.json"
input_network = DATA_EXCEPTION_SET / "input_network_data.json"
active_power_profile = DATA_EXCEPTION_SET / "active_power_profile.parquet"
ev_active_power_profile = DATA_EXCEPTION_SET / "ev_active_power_profile.parquet"

P = 75
Seed = 34


EV.ev_penetration(input_network, metadata, active_power_profile, ev_active_power_profile, P, Seed)
