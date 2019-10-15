import yaml
import re


class RallyConfiguration:
    rally_configuration = None

    def __init__(self, team_name):
        config_file_name = team_name.lower() + "_rally_config.yml"
        with open("config/" + config_file_name, 'r') as stream:
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

    def cycle_time_start_states(self):
        return self.prepare_flow_state_list(self.rally_configuration["board"]["cycleTime"]["startState"])

    def cycle_time_end_states(self):
        return self.prepare_flow_state_list(self.rally_configuration["board"]["cycleTime"]["endState"])

    def story_creation_start_date(self):
        return self.rally_configuration["board"]["story"]["creationDate"]

    def proxy(self):
        return self.rally_configuration["proxy"]

    @staticmethod
    def prepare_flow_state_list(states):
        if states.index(',') > -1:
            return map(str.strip, states.split(','))
        else:
            return {states}

    @staticmethod
    def strip_whitespaces(self, x):
        return x.strip()
