import pytest

from power_system_simulation.power_system_simulation import *
#wrong metadata
metadata_transformers = "src\\data\\input\\new_test_data\\Exception_test_data\\meta_data_transformers.json"
metadata_Sources = "src\\data\\input\\new_test_data\\Exception_test_data\\meta_data_source.json"

#weong Input network
input_network_feeders = "src\\data\\input\\new_test_data\\Exception_test_data\\input_network_data_feederID.json"
input_network_feederTransformer = "src\\data\\input\\new_test_data\\Exception_test_data\\input_network_data_feederTransformer.json"


#correct input data
metadata = "src\\data\\input\\new_test_data\\input\\meta_data.json"
input_network = "src\\data\\input\\new_test_data\\input\\input_network_data.json"
active_power_profile = "src\\data\\input\\new_test_data\\input\\active_power_profile.parquet"
reactive_power_profile = "src\\data\\input\\new_test_data\\input\\reactive_power_profile.parquet"
ev_active_power_profile = "src\\data\\input\\new_test_data\\input\\ev_active_power_profile.parquet"

power_system_simulation.__init__(input_network, metadata, active_power_profile, reactive_power_profile,ev_active_power_profile)

def test_TooManyTransformers():
    with pytest.raises(TooManyTransformers):
        power_system_simulation.__init__(input_network, metadata_transformers, active_power_profile, reactive_power_profile,ev_active_power_profile)

def test_TooManySources():
    with pytest.raises(TooManySources):
        power_system_simulation.__init__(input_network, metadata_Sources, active_power_profile, reactive_power_profile,ev_active_power_profile)

def test_NotAllFeederIDsareValid():
    with pytest.raises(NotAllFeederIDsareValid):
        power_system_simulation.__init__(input_network_feeders, metadata, active_power_profile, reactive_power_profile,ev_active_power_profile)

def test_TransformerAndFeedersnotconnected():
    with pytest.raises(TransformerAndFeedersnotconnected):
        power_system_simulation.__init__(input_network_feederTransformer, metadata, active_power_profile, reactive_power_profile,ev_active_power_profile)

def test_TooFewEVs():
    pass