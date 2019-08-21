import pendulum
from revision_history_parser import RevisionHistoryParser
from rally_configuration import RallyConfiguration


class Story:

    def __init__(self, rally_story, flow_states):
        self.name = rally_story.Name
        self.id = rally_story.FormattedID
        self.schedule_state = rally_story.ScheduleState
        self.points = rally_story.PlanEstimate
        self.flow_state_changes = self.get_flow_state_changes(rally_story.RevisionHistory.Revisions, flow_states)
        self.cycle_time = self.cycle_time()

    def get_flow_state_changes(self, rally_revisions, flow_states):
        flow_state_changes = {}
        for item in flow_states:
            for revision in rally_revisions:
                if RevisionHistoryParser.is_line_for_this_state_change(revision.Description, item):
                    flow_state_changes[item] = revision.CreationDate
        return flow_state_changes

    def cycle_time(self):
        result = ''
        start_state = RallyConfiguration().cycle_time_start_state()
        end_state = RallyConfiguration().cycle_time_end_state()
        if self.flow_state_changes.get(start_state) is not None \
                and self.flow_state_changes.get(end_state) is not None:
            temp = pendulum.parse(self.flow_state_changes.get(end_state)) - pendulum.parse(
                self.flow_state_changes.get(start_state))
            result = str(temp._days)
        return result
