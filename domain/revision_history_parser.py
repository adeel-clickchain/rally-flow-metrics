import re

class RevisionHistoryParser:

    @staticmethod
    def is_revision_for_state_change(line, states):
        if line is None:
            return False
        for state in states:
            state = re.escape(state)
            revision_change_regular_expression = re.compile(r'([A-Z ]+) STATE changed from \[(.*)\] to \[' + state + ']')
            match = revision_change_regular_expression.search(line)
            if match:
                return True
