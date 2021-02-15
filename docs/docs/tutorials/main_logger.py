# main.py
import os

import openhtf as htf
from openhtf.plugs.user_input import UserInput
from spintop_openhtf import TestPlan

""" Test Plan """

# This defines the name of the testbench.
plan = TestPlan('hello')

@plan.testcase('Logger Test')
def logger_test(test):
    test.logger.info('This is a logging test string')
    
if __name__ == '__main__':
    plan.run()