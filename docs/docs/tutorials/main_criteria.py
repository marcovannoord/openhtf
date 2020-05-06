# main.py
import os

import openhtf as htf
from spintop_openhtf import TestPlan
from pprint import pprint


""" Test Plan """

# This defines the name of the testbench.
plan = TestPlan('Criteria')

criterion = htf.Measurement('test_criterion').in_range(18, 22)

@plan.testcase('Criteria test')
@htf.measures(criterion)
def criteria_test(test): 
    value = 12
    test.measurements.test_criterion = value	
    
   
if __name__ == '__main__':
    plan.run()