import csv
import pendulum
import logging
import os
from pyral import Rally
from statistics import mean
import argparse

from rally_configuration import RallyConfiguration
from story import Story
from revision_history_parser import RevisionHistoryParser

logging.getLogger().setLevel(logging.INFO)
rally_configuration = RallyConfiguration()


def publish_continuous_flow_metrics(report_start_date, report_end_date):
    existing_flow_states = find_flow_state_names()
    stories = find_stories_in_rally(report_start_date, report_end_date, existing_flow_states)
    write_to_csv_file(report_start_date, report_end_date, stories, existing_flow_states)


def find_stories_in_rally(report_start_date, report_end_date, existing_flow_states):
    stories = list()
    fields = "FormattedID, ScheduleState, PlanEstimate, State, " \
             "Name, CreationDate, RevisionHistory, Revisions, FlowState"
    query = "CreationDate >= " + rally_configuration.story_creation_start_date().__str__()
    rally_stories = rally_instance().get('UserStory', fields=fields, query=query, instance=True)

    for rally_story in rally_stories:
        if (story_deployed_recently(rally_story, report_start_date, report_end_date)
                or story_is_in_progress(rally_story, report_end_date)):
            stories.append(Story(rally_story, existing_flow_states))
    return stories


def find_flow_state_names():
    flow_states = rally_instance().get("FlowState")
    flow_states_names = []
    for flow_state in flow_states:
        if flow_state.Name != 'Ready' and flow_state.Name != 'Backlog':
            flow_states_names.append(flow_state.Name)
    return flow_states_names


def story_deployed_recently(story, report_start_date, report_end_date):
    for revision in story.RevisionHistory.Revisions:
        if RevisionHistoryParser.is_line_for_this_state_change(revision.Description,
                                                               RallyConfiguration().cycle_time_end_state()):
            if pendulum.parse(report_start_date) <= pendulum.parse(revision.CreationDate) <= pendulum.parse(
                    report_end_date):
                return True


def story_is_in_progress(rally_story, report_end_date):
    if rally_story.ScheduleState == 'In-Progress' and (
            pendulum.parse(report_end_date) >= pendulum.parse(rally_story.InProgressDate)):
        return True


def write_to_csv_file(report_start_date, report_end_date, stories, flow_states):
    create_reports_folder_if_it_doesnt_exist()
    with open("reports/" + RallyConfiguration().project_name().replace(" ", "_").lower() + "_rally_metrics.csv", 'w',
              newline='') as csv_file:
        output = csv.writer(csv_file)
        output.writerow(create_header_row(flow_states))
        for story in stories:
            output.writerow(create_data_row(story, flow_states))
        summary = Summary(stories)
        output.writerow("")
        output.writerow(['Team Name:', rally_configuration.project_name()])
        output.writerow(['Report Start Date:', report_start_date])
        output.writerow(['Report End Date', report_end_date])
        output.writerow(['Throughput', summary.throughput])
        output.writerow(['Mean Cycle Time', summary.mean_cycle_time])


def create_reports_folder_if_it_doesnt_exist():
    directory = "reports"
    if not os.path.exists(directory):
        os.makedirs(directory)


def create_data_row(story, flow_states):
    data = [story.id, story.name]
    for flow_state in flow_states:
        data.append(story.flow_state_changes.get(flow_state))
    data.append(story.cycle_time)
    return data


def create_header_row(flows_states):
    headers = ["STORY ID", "STORY DESCRIPTION"]
    for flows_state in flows_states:
        headers.append(flows_state.upper())
    headers.append("CYCLE TIME")
    return headers


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


class Summary:
    def __init__(self, stories):
        self.mean_cycle_time = self.get_mean_cycle_time(stories)
        self.throughput = self.get_through_put(stories)

    def get_mean_cycle_time(self, stories):
        cycle_times = list()
        for story in stories:
            if story.cycle_time is not None:
                cycle_times.append(story.cycle_time)
        return mean(cycle_times)

    def get_through_put(self, stories):
        throughput = 0
        for story in stories:
            if story.cycle_time is not None:
                throughput = throughput + 1
        return throughput


def configure_arguments():
    global args
    # initiate the parser
    parser = argparse.ArgumentParser()
    # add long and short argument
    parser.add_argument("--report_start_date", "-s", help="The start date of the report")
    parser.add_argument("--report_end_date", "-e", help="The end date of the report")
    args = parser.parse_args()


def configure_proxy():
    if rally_configuration.proxy() is not None:
        os.environ['HTTPS_PROXY'] = "proxyvipecc.nb.ford.com:83"


if __name__ == "__main__":
    configure_proxy()
    configure_arguments()
    publish_continuous_flow_metrics(args.report_start_date, args.report_end_date)
