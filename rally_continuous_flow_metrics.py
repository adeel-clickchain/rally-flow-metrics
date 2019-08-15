from pyral import Rally
import re
import csv
import pendulum
import logging
import yaml
import os

logging.getLogger().setLevel(logging.INFO)


def publish_continuous_flow_metrics():
    stories = find_deployed_stories()
    write_to_csv_file(stories)


def find_deployed_stories():
    existing_flow_states = find_flow_state_names()
    report_start_date = "2019-01-01"
    report_end_date = "2019-08-15"
    rally_configuration = RallyConfiguration()
    deployed_stories = list()
    fields = "FormattedID, ScheduleState, PlanEstimate, State, " \
             "Name, CreationDate, RevisionHistory, Revisions, FlowState"
    query = "CreationDate >= " + rally_configuration.story_creation_start_date().__str__()
    rally_stories = rally_instance().get('UserStory', fields=fields, query=query, instance=True)
    for rally_story in rally_stories:
        #if check_time_range(rally_story, report_start_date, report_end_date):
        deployed_stories.append(Story(rally_story, existing_flow_states))
    return deployed_stories


def find_flow_state_names():
    flow_states = rally_instance().get("FlowState")
    flow_states_names = []
    for flow_state in flow_states:
        flow_states_names.append(flow_state.Name)
    return flow_states_names


def check_time_range(story, report_start_date, report_end_date):
    for revision in story.RevisionHistory.Revisions:
        if Parser.parse_line_check_state(revision.Description, RallyConfiguration().cycle_time_end_state()):
            if pendulum.parse(report_start_date) <= pendulum.parse(revision.CreationDate) <= pendulum.parse(
                    report_end_date):
                return True


def write_to_csv_file(stories):
    with open("reports/" + RallyConfiguration().project_name().replace(" ", "_").lower() + "_rally_metrics.csv", 'w', newline='') as csv_file:
        output = csv.writer(csv_file)
        output.writerow(["STORY ID", "Story DESCRIPTION", "IN-PROGRESS", "COMPLETED",
                         "DEPLOYED TO STAGE/PERF",  "DONE [DEPLOYED TO PROD]", "CYCLE TIME"])
        for story in stories:
            output.writerow([story.id,
                             story.name,
                             story.flow_state_changes.get(RallyConfiguration().cycle_time_start_state()),
                             story.flow_state_changes.get('COMPLETED'),
                             story.flow_state_changes.get('DEPLOYED TO STAGE/PERF'),
                             story.flow_state_changes.get(RallyConfiguration().cycle_time_end_state()),
                             story.cycle_time])


def rally_instance():
    os.environ.get('HTTPS_PROXY', None)
    rally_configuration = RallyConfiguration()
    return Rally(server=rally_configuration.server_uri(),
                 apikey=rally_configuration.api_key(),
                 project=rally_configuration.project_name(),
                 workspace=rally_configuration.work_space(),
                 )


class Parser:

    @staticmethod
    def parse_line_check_state(line, state):
        state = re.escape(state)
        revision_change_regular_expression = re.compile(r'([A-Z ]+) STATE changed from \[(.*)\] to \[' + state + '\]')
        match = revision_change_regular_expression.search(line)
        if match:
            return True


class Revisions:
    def __init__(self, revision, state):
        self.created = revision.CreationDate
        self.state = state


class Story:

    def __init__(self, rally_story, flow_states):
        self.name = rally_story.Name
        self.id = rally_story.FormattedID
        self.schedule_state = rally_story.ScheduleState
        self.points = rally_story.PlanEstimate
        self.flow_state_changes = self.get_flow_state_changes(rally_story.RevisionHistory.Revisions, flow_states)
        self.cycle_time = self.get_cycle_time()

    def get_flow_state_changes(self, rally_revisions, flow_states):
        flow_state_changes = {}
        for item in flow_states:
            for revision in rally_revisions:
                if Parser.parse_line_check_state(revision.Description, item):
                    flow_state_changes[item] = revision.CreationDate
        return flow_state_changes

    def get_cycle_time(self):
        result = ''
        start_state = RallyConfiguration().cycle_time_start_state()
        end_state = RallyConfiguration().cycle_time_end_state()
        if self.flow_state_changes.get(start_state) is not None \
                and self.flow_state_changes.get(end_state) is not None:
            temp = pendulum.parse(self.flow_state_changes.get(end_state)) - pendulum.parse(
                self.flow_state_changes.get(start_state))
            result = str(temp._days)
        return result


class RallyConfiguration:

    rally_configuration = None

    def __init__(self):
        with open("rally_config.yml", 'r') as stream:
            try:
                self.rally_configuration = yaml.safe_load(stream)["rally"]
            except yaml.YAMLError as exc:
                print(exc)

    def server_uri(self):
        return self.rally_configuration["uri"]

    def api_key(self):
        return self.rally_configuration["apikey"]

    def project_name(self):
        return self.rally_configuration["project"]

    def work_space(self):
        return self.rally_configuration["workspace"]

    def cycle_time_start_state(self):
        return self.rally_configuration["board"]["cycleTime"]["startState"]

    def cycle_time_end_state(self):
        return self.rally_configuration["board"]["cycleTime"]["endState"]

    def story_creation_start_date(self):
        return self.rally_configuration["board"]["story"]["creationDate"]

    def proxy(self):
        return self.rally_configuration["proxy"]


if __name__ == "__main__":
    if RallyConfiguration().proxy() is not None:
        os.environ['HTTPS_PROXY'] = "proxyvipecc.nb.ford.com:83"
    publish_continuous_flow_metrics()
