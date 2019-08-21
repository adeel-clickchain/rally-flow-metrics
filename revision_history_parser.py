import re


class RevisionHistoryParser:

    @staticmethod
    def is_line_for_this_state_change(line, state):
        if line is None:
            return False
        state = re.escape(state)
        revision_change_regular_expression = re.compile(r'([A-Z ]+) STATE changed from \[(.*)\] to \[' + state + ']')
        match = revision_change_regular_expression.search(line)
        if match:
            return True
