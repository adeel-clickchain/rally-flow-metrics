from domain.rally_configuration import RallyConfiguration


def test_rally_configuration_can_provide_multiple_start_states():
    rally_configuration = RallyConfiguration("navigation")
    assert sorted(rally_configuration.cycle_time_start_states()) == sorted({'IN PROGRESS', 'DEFINED'})


def test_rally_configuration_can_provide_multiple_end_states():
    rally_configuration = RallyConfiguration("navigation")
    assert sorted(rally_configuration.cycle_time_end_states()) == sorted({'ALMOST DONE', 'DONE'})


def test_rally_configuration_can_provide_end_state_with_spaces():
    rally_configuration = RallyConfiguration("loyalty")
    assert sorted(rally_configuration.cycle_time_start_states()) == sorted({'Development'})