import copy
import json
import pprint
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import pytest
from IPython.display import display

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


def test_Nm1_scenario_class():
    assert nm_file.nm_function(
        18, input_network_path, metadata_path, active_power_profile_path, reactive_power_profile_path
    ) == [24]
    """assert(nm1.Nm_scenario_class(17,input_network_path,metadata_path,active_power_profile_path,reactive_power_profile_path)==[])
    assert(nm1.Nm_scenario_class(23,input_network_path,metadata_path,active_power_profile_path,reactive_power_profile_path)==[])
    assert(nm1.Nm_scenario_class(20,input_network_path,metadata_path,active_power_profile_path,reactive_power_profile_path)==[24])"""
