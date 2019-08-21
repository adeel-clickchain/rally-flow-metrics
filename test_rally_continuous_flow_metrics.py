import pytest
def test_file1_method1():
	x=5
	y=6
	assert x+1 == y,"test failed"
	assert x == y,"test failed"
def test_file1_method2():
	x=5
	y=6
	assert x+1 == y,"test failed"


#import pytest
#from rally_continuous_flow_metrics import Story, Parser

#class RallyContinuousFlowMetricsTests():

 #   def test_current_iteration_if_today_within_start_and_end_date(iteration):
  #      assert True is True

    # def test_when_deployed_state_then_parse_successfully(self):
    #     line = 'FLOW STATE CHANGED DATE changed from [Fri Aug 02 08:36:58 MDT 2019] to [Mon Aug 05 13:29:00 MDT 2019], FLOW STATE changed from [Ready For Prod] to [Deployed]'
    #     state = 'Deployed'
    #     self.assertEqual(True, Parser.parse_line_check_state(line, state))
    #
    # def test_when_deployed_state_name_has_special_characters_then_parse_successfully(self):
    #     line = 'FLOW STATE CHANGED DATE changed from [Tue Jul 02 13:51:45 MDT 2019] to [Fri Aug 09 14:31:57 MDT 2019], FLOW STATE changed from [DEPLOYED TO STAGE/PERF] to [DONE [DEPLOYED TO PROD]]'
    #     state = rally_continuous_flow_metrics.RallyConfiguration().cycle_time_end_state()
    #     self.assertEqual(True, Parser.parse_line_check_state(line, state))
    #
    # def test_cycle_time_reports_work_days(self):
    #     story = Story()
    #     self.assertEqual(5, story.get_cycle_time())