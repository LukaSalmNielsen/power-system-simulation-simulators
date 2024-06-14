import unittest
import pytest
import json
import time
import copy
from typing import Dict
from IPython.display import display
import pprint
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import networkx as nx
import matplotlib.pyplot as plt

import power_system_simulation.Nm_calculation as nm_file
######################################################################
# Data path handling (used for calling the class Nm1_calculation.py) #
######################################################################

DATA_PATH = Path(__file__).parent / "data"
DATA_EXCEPTION_SET = DATA_PATH / "Exception_test_data"
metadata_path = DATA_EXCEPTION_SET / "meta_data.json"
input_network_path = DATA_EXCEPTION_SET / "input_network_data.json"
active_power_profile_path = DATA_EXCEPTION_SET / "active_power_profile.parquet"
reactive_power_profile_path = DATA_EXCEPTION_SET / "reactive_power_profile.parquet"


## Test1. ID not valid error

## Test3.
def test_Nm1_scenario_class():
    assert(nm_file.Nm_function(18,input_network_path,metadata_path,active_power_profile_path,reactive_power_profile_path)==[24])
    """assert(nm1.Nm_scenario_class(17,input_network_path,metadata_path,active_power_profile_path,reactive_power_profile_path)==[])
    assert(nm1.Nm_scenario_class(23,input_network_path,metadata_path,active_power_profile_path,reactive_power_profile_path)==[])
    assert(nm1.Nm_scenario_class(20,input_network_path,metadata_path,active_power_profile_path,reactive_power_profile_path)==[24])"""