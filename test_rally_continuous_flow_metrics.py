import pytest
from revision_history_parser import RevisionHistoryParser
from story import Story
import pendulum


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def test_when_deployed_state_then_parse_successfully():
    line = 'FLOW STATE CHANGED DATE changed from [Fri Aug 02 08:36:58 MDT 2019] ' \
           'to [Mon Aug 05 13:29:00 MDT 2019], FLOW STATE changed from [Ready For Prod] ' \
           'to [Deployed]'
    state = 'Deployed'
    assert RevisionHistoryParser.is_line_for_this_state_change(line, state) is True


def test_when_deployed_state_name_has_special_characters_then_parse_successfully():
    line = 'FLOW STATE CHANGED DATE changed from [Tue Jul 02 13:51:45 MDT 2019] ' \
           'to [Fri Aug 09 14:31:57 MDT 2019], FLOW STATE changed from [DEPLOYED TO STAGE/PERF] ' \
           'to [DONE [DEPLOYED TO PROD]]'
    state = 'DONE [DEPLOYED TO PROD]'
    assert RevisionHistoryParser.is_line_for_this_state_change(line, state) is True


@pytest.fixture()
def deployed_story_over_the_weekend():
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
    return Story(rally_story, ['Backlog', 'To-Do', 'In-Progress', 'Completed', 'Ready For Prod', 'Deployed'])


def test_cycle_time_only_includes_business_days(deployed_story_over_the_weekend):
    assert deployed_story_over_the_weekend.cycle_time == 4
