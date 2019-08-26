import csv
import pendulum
import logging
import os
from pyral import Rally

from rally_configuration import RallyConfiguration
from story import Story
from revision_history_parser import RevisionHistoryParser

logging.getLogger().setLevel(logging.INFO)
rally_configuration = RallyConfiguration()


def publish_continuous_flow_metrics():
    stories = find_deployed_stories()
    write_to_csv_file(stories)


def find_deployed_stories():
    existing_flow_states = find_flow_state_names()
    report_start_date = "2019-08-12"
    report_end_date = "2019-08-18"
    deployed_stories = list()
    fields = "FormattedID, ScheduleState, PlanEstimate, State, " \
             "Name, CreationDate, RevisionHistory, Revisions, FlowState"
    query = "CreationDate >= " + rally_configuration.story_creation_start_date().__str__()
    rally_stories = rally_instance().get('UserStory', fields=fields, query=query, instance=True)
    for rally_story in rally_stories:
        if check_time_range(rally_story, report_start_date, report_end_date):
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
        if RevisionHistoryParser.is_line_for_this_state_change(revision.Description,
                                                               RallyConfiguration().cycle_time_end_state()):
            if pendulum.parse(report_start_date) <= pendulum.parse(revision.CreationDate) <= pendulum.parse(
                    report_end_date):
                return True


def write_to_csv_file(stories):
    with open("reports/" + RallyConfiguration().project_name().replace(" ", "_").lower() + "_rally_metrics.csv", 'w',
              newline='') as csv_file:
        output = csv.writer(csv_file)
        output.writerow(["STORY ID", "STORY DESCRIPTION", "DOING",
                         "DONE", "CYCLE TIME"])
        for story in stories:
            output.writerow([story.id,
                             story.name,
                             story.flow_state_changes.get(RallyConfiguration().cycle_time_start_state()),
                             story.flow_state_changes.get(RallyConfiguration().cycle_time_end_state()),
                             story.cycle_time])


def rally_instance():
    os.environ.get('HTTPS_PROXY', None)
    return Rally(server=rally_configuration.server_uri(),
                 apikey=rally_configuration.api_key(),
                 project=rally_configuration.project_name(),
                 workspace=rally_configuration.work_space(),
                 )


class Revisions:
    def __init__(self, revision, state):
        self.created = revision.CreationDate
        self.state = state


if __name__ == "__main__":
    if rally_configuration.proxy() is not None:
        os.environ['HTTPS_PROXY'] = "proxyvipecc.nb.ford.com:83"
    publish_continuous_flow_metrics()
