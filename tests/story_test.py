import pytest
from domain.story import Story
from tests.dot_dictionary import DotDict

@pytest.fixture()
def deployed_story_over_a_weekend():
    revision_0 = DotDict({
        'CreationDate': "2019-07-11T14:33:20.000Z"
    })
    revision_1 = DotDict({
        'CreationDate': "2019-07-31T15:33:20.000Z",
        'Description': "SCHEDULE STATE changed from [To-Do] to [In-Progress], READY changed from [true] to [false]"
    })
    revision_2 = DotDict({
        'CreationDate': "2019-08-06T16:33:20.000Z",
        'Description': "SCHEDULE STATE changed from [Ready For Prod] to [Deployed]"
    })
    rally_story = DotDict({
        'ScheduleState': 'Completed',
        'RevisionHistory': DotDict({
            'Revisions': [revision_2, revision_1, revision_0]
        })
    });
    return Story(rally_story, ['Backlog', 'To-Do', 'In-Progress', 'Completed', 'Ready For Prod', 'Deployed'],
                 {'In-Progress', 'Development'}, {'Deployed', 'Prod - ON'})


def test_cycle_time_only_includes_business_days(deployed_story_over_a_weekend):
    assert deployed_story_over_a_weekend.cycle_time == 7


def test_find_current_start_state() :
    assert 'In-Progress' == Story.find_current_state_name({'Backlog', 'To-Do', 'In-Progress', 'Completed', 'Ready For Prod', 'Deployed'}, {'In-Progress', 'Development'})
