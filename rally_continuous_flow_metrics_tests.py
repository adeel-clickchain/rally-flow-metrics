import unittest
import rally_continuous_flow_metrics

class MyTestCase(unittest.TestCase):

    def when_deployed_state_parse_successfully(self):
        line='FLOW STATE CHANGED DATE changed from [Fri Aug 02 08:36:58 MDT 2019] to [Mon Aug 05 13:29:00 MDT 2019], FLOW STATE changed from [Ready For Prod] to [Deployed]'
        state='Deployed'
        self.assertEqual(True, rally_continuous_flow_metrics.Parser.parse_line_check_state(line, state))


if __name__ == '__main__':
    unittest.main()
