Clone the repo at: https://github.com/adeel-clickchain/rally-flow-metrics.git

Please visit the following website to download python 3.6.3 version: https://www.python.org/downloads/

Commands for creating virtual environment after installing python on the system are:
~~~ bash
pip install virtualenv
~~~

To create a virtual environment, you must specify a path. For example to create one in the local directory called ‘mypython’, type the following:  
~~~ bash
virtualenv mypython
~~~

You can activate the python environment by running the following command:  
~~~ bash
source mypython/bin/activate
~~~

Run the following command to install the project related modules and libraries:
~~~ bash
pip install -r requirements.txt
~~~

Create a configuration file under the "config" folder named [Team Name]_rally_config.yml e.g. navigation_rally_config.yml. 
Here is a sample configuration:

~~~ bash
rally:
  uri: [URL for Rally]
  apikey: [API key received from Rally, see https://docs.ca.com/en-us/ca-agile-central/saas/rally-application-manager]
  proxy: [Proxy URI if necessary, otherwise keep blank]
  project: [Name of the project in Rally]
  workspace: [Name of the workspace in Rally]
  board:
    cycleTime:
      startState: [Name of the cycle time start flow state in rally team board]
      endState: [Name of the cycle time end flow state in rally team board]
    story:
      creationDate: [Provide the earliest creation date for stories in rally in YYYY-MM-DD format]
~~~

Run the python script named rally_continuous_flow_metrics passing in the team name, report start and end date as arguments. Please note that the team name should correspond with the name used to create the configuration file. Here are a few examples:

~~~ bash
py rally_continuous_flow_metrics.py -t [Team Name] -s [Report Start Date YYYY-MM-DD] -e [Report End Date YYYY-MM-DD]

e.g. py rally_continuous_flow_metrics.py -t navigation -s 2019-09-16 -e 2019-09-22
     py rally_continuous_flow_metrics.py -t assist -s 2019-09-23 -e 2019-09-29
~~~

The report will be generated under the "reports" folder with the name [team name]_[start date]_[end_date]_metrics.csv e.g. assist_2019-09-23_2019-09-29_metrics.csv