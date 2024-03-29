import pendulum
from domain.revision_history_parser import RevisionHistoryParser


class Story:

    def __init__(self, rally_story, flow_states, configured_start_states, configured_end_states):
        self.name = rally_story.Name
        self.id = rally_story.FormattedID
        self.schedule_state = rally_story.ScheduleState
        self.points = rally_story.PlanEstimate
        self.flow_state_changes = self.get_flow_state_changes(rally_story.RevisionHistory.Revisions, flow_states)
        self.cycle_time = self.cycle_time(Story.find_current_state_name(flow_states, configured_start_states)
                                          , Story.find_current_state_name(flow_states, configured_end_states))

    def get_flow_state_changes(self, rally_revisions, flow_states):
        flow_state_changes = {}
        for item in flow_states:
            for revision in rally_revisions:
                if RevisionHistoryParser.is_revision_for_state_change(revision.Description, {item}):
                    flow_state_changes[item] = revision.CreationDate
        return flow_state_changes

    def cycle_time(self, start_state, end_state):
        if self.flow_state_changes.get(start_state) is not None \
                and self.flow_state_changes.get(end_state) is not None:
            start_date = pendulum.parse(
                self.flow_state_changes.get(start_state))
            end_date = pendulum.parse(self.flow_state_changes.get(end_state))
            period = pendulum.period(start_date, end_date)
            return period.in_days() + 1

    @staticmethod
    def find_current_state_name(flow_state_names, configured_state_names):
        for state in configured_state_names:
            if state in flow_state_names:
                return state

