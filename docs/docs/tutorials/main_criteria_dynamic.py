# main.py
import os

import openhtf as htf
from spintop_openhtf import TestPlan
from pprint import pprint
from criteria import get_criteria
from product import voltage


""" Test Plan """

# This defines the name of the testbench.
plan = TestPlan('Criteria')

@plan.testcase('Dynamic Criterion Test', requires_state=True)
def criteria_test(state):
    value = 12
    state.running_phase_state.measurements['VOLTAGE'] = htf.Measurement('VOLTAGE').in_range(11.5,12.5)
    state.test_api.measurements.VOLTAGE = value	
    
@plan.testcase('Dynamic Criterion Test from Product Definition', requires_state=True)
def product_definition_test(state):
    value = 12
    state.running_phase_state.measurements['INPUT_VOLTAGE'] = htf.Measurement('INPUT_VOLTAGE').in_range(voltage.input_voltage - 0.5, voltage.input_voltage + 0.5)
    state.test_api.measurements.INPUT_VOLTAGE = value	
    
@plan.testcase('Dynamic Criterion Test from Previous Measurement', requires_state=True)
def previous_measurement_test(state):

    #measured_input = measure_input_voltage()
    measured_input = 12.05 
    
    #divider_voltage = measure_divider_voltage()
    divider_voltage = 3.55
    
    #definition of criterion
    state.running_phase_state.measurements['DIVIDER_VOLTAGE'] = htf.Measurement('DIVIDER_VOLTAGE').in_range(measured_input * 0.3 * 0.95, measured_input * 0.3 * 1.05)
    
    #evaluation of criterion
    state.test_api.measurements.DIVIDER_VOLTAGE = divider_voltage	
    
      
    
if __name__ == '__main__':
    plan.run()