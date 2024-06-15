## Test2. Edge already disconnected


def test_edge_already_disconn(self):
    with self.assertRaises(Exception):
        Nm1_scenario_calculation(24, input_data, active_power_profile, reactive_power_profile)
