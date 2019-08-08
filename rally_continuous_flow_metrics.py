from pyral import Rally
import re
import csv
import pendulum
import logging
import yaml

logging.getLogger().setLevel(logging.INFO)
report_start_date = "2019-07-21"
report_end_date = "2019-08-03"


def publish_continuous_flow_metrics():
    stories = find_deployed_stories()
    write_to_csv_file(stories)


def find_deployed_stories():
    deployed_stories = []
    fields = "FormattedID,ScheduleState,PlanEstimate,State,Name,CreationDate,RevisionHistory,Revisions,FlowState"
    query = "CreationDate >= 2019-05-01"
    stories = rally_instance().get('UserStory', fields=fields, query=query, instance=True)
    existing_flow_states = find_flow_state_names()
    for story in stories:
        if check_time_range(story):
            logging.info("making story object for " + story.FormattedID)
            deployed_stories.append(Story(story, existing_flow_states))
    return deployed_stories


def find_flow_state_names():
    flow_states = rally_instance().get("FlowState")
    logging.info("getting flow states")
    flow_states_names = []
    for flow_state in flow_states:
        flow_states_names.append(flow_state.Name)
    return flow_states_names


def check_time_range(story):
    for revision in story.RevisionHistory.Revisions:
        if Parser.parse_line_check_state(revision.Description, rally_cycle_time_end_state()):
            if pendulum.parse(report_start_date) <= pendulum.parse(revision.CreationDate) <= pendulum.parse(
                    report_end_date):
                return True


def write_to_csv_file(stories):
    logging.info("creating CSV")
    with open("rally_metrics.csv", 'w', newline='') as csv_file:
        output = csv.writer(csv_file)
        output.writerow(["Story ID", "Story", "Doing", "Done", "Cycle Time"])
        for story in stories:
            output.writerow([story.id, story.name, story.revisions["revisions"].get(rally_cycle_time_start_state()),
                             story.revisions["revisions"].get(rally_cycle_time_end_state()), story.cycle_time()])
        logging.info("CSV created")


def rally_instance():
    rally_configuration = RallyConfiguration()
    return Rally(server=rally_configuration.server_uri(),
                 apikey=rally_configuration.api_key(),
                 project=rally_configuration.project_name(),
                 workspace=rally_configuration.work_space())


class Parser:

    @staticmethod
    def parse_line_check_state(line, state):
        revision_change_regular_expression = re.compile(r'([A-Z ]+) changed from \[(.*)\] to \[' + state + '\]')
        match = revision_change_regular_expression.search(line)
        if match:
            return True


class Revisions:
    def __init__(self, revision, state):
        self.created = revision.CreationDate
        self.state = state


class Story:
    revisions = {}

    def __init__(self, story, flow_states):
        self.revisions["revisions"] = self.create_revision_based_on_state(flow_states, story.RevisionHistory.Revisions)
        self.name = story.Name
        self.id = story.FormattedID
        self.schedule_state = story.ScheduleState
        self.points = story.PlanEstimate

    @staticmethod
    def create_revision_based_on_state(flow_states, revisions):
        temp = {}
        for item in flow_states:
            for revision in revisions:
                if Parser.parse_line_check_state(revision.Description, item):
                    temp[item] = revision.CreationDate
        return temp

    def cycle_time(self):
        result = ""
        if self.revisions["revisions"].get(rally_cycle_time_start_state()) is not None \
                and self.revisions["revisions"].get(rally_cycle_time_end_state()) is not None:
            temp = pendulum.parse(self.revisions["revisions"].get(rally_cycle_time_end_state())) - pendulum.parse(
                self.revisions["revisions"].get(rally_cycle_time_end_state()))
            result = str(temp._days)
        return result


class RallyConfiguration:

    rally_configuration = None

    def __init__(self):
        with open("rally_config.yml", 'r') as stream:
            try:
                self.rally_configuration = yaml.safe_load(stream)
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


if __name__ == "__main__":
    publish_continuous_flow_metrics()
