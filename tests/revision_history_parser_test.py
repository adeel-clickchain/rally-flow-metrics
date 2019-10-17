from domain.revision_history_parser import RevisionHistoryParser


def test_when_deployed_state_then_parse_successfully():
    line = 'FLOW STATE CHANGED DATE changed from [Fri Aug 02 08:36:58 MDT 2019] ' \
           'to [Mon Aug 05 13:29:00 MDT 2019], FLOW STATE changed from [Ready For Prod] ' \
           'to [Deployed]'
    state = 'Deployed'
    assert RevisionHistoryParser.is_revision_for_state_change(line, {state}) is True


def test_when_deployed_state_name_has_special_characters_then_parse_successfully():
    line = 'FLOW STATE CHANGED DATE changed from [Tue Jul 02 13:51:45 MDT 2019] ' \
           'to [Fri Aug 09 14:31:57 MDT 2019], FLOW STATE changed from [DEPLOYED TO STAGE/PERF] ' \
           'to [DONE [DEPLOYED TO PROD]]'
    state = 'DONE [DEPLOYED TO PROD]'
    assert RevisionHistoryParser.is_revision_for_state_change(line, {state}) is True


def test_when_state_name_changes_revision_is_identified():
    line = 'FLOW STATE CHANGED DATE changed from [Tue Jul 02 13:51:45 MDT 2019] ' \
           'to [Fri Aug 09 14:31:57 MDT 2019], FLOW STATE changed from [DEPLOYED TO STAGE/PERF] ' \
           'to [DONE [DEPLOYED TO PROD]]'
    state = {'DONE [DEPLOYED TO PROD]', 'COMPLETED'}
    assert RevisionHistoryParser.is_revision_for_state_change(line, state) is True