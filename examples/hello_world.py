import time
import random

from spintop_openhtf import TestPlan

import openhtf as htf
from openhtf.util import conf

""" Test Plan """

plan = TestPlan()
# plan.define_top_level_component('nets.yml')

@plan.testcase('Hello-World')
def hello_world(test):
    """ Find the bluetooth device """
    test.logger.info('Hello World')

if __name__ == '__main__':
    conf.load(station_server_port='4444')
    plan.run()




