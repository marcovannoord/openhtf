# main.py
import os

import openhtf as htf
from spintop_openhtf import TestPlan
from pprint import pprint
from criteria import get_criteria


""" Test Plan """

# This defines the name of the testbench.
plan = TestPlan('Criteria')

@plan.testcase('Criteria test')
@htf.measures(get_criteria('test_criterion'))
def criteria_test(test):
    value = 20
    test.measurements.test_criterion = value	
    

   
if __name__ == '__main__':
    plan.run()