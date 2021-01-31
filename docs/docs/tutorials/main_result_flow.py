# main.py
import os

import random
import openhtf as htf
from openhtf import PhaseResult
from openhtf.plugs.user_input import UserInput
from spintop_openhtf import TestPlan
from pprint import pprint
from time import sleep

from static import SleepConfig

from openhtf.util import conf

FORM_LAYOUT = {
    'schema':{
        'title': "Test configuration",
        'type': "object",
        'required': ['operator', 'dutid', 'product'],
        'properties': {
            'operator': {
                'type': "string", 
                'title': "Enter the operator name"
            },
            'dutid': {
                'type': "string", 
                'title': "Enter the device under test serial number"
            },
            'product': {
                'type': "string", 
                'title': "Enter the product name"
            }
        }
    },
    'layout':[
        "operator", "dutid", "product",
    ]
}

""" Test Plan """

# This defines the name of the testbench.
plan = TestPlan('hello')

@plan.trigger('Configuration')
@plan.plug(prompts=UserInput)
def trigger(test, prompts):
    """Displays the configuration form"""
    response = prompts.prompt_form(FORM_LAYOUT)
    test.dut_id = response['dutid']
    test.state["operator"] = response['operator']
    test.state["product"] = response['product']
    pprint (response)
    
@plan.testcase('Sleep')
def sleep_test(test):
    """Waits five seconds"""
    sleep(5)
    if test.state["product"] == "A":
        return PhaseResult.CONTINUE
    elif test.state["product"] == "B":
        return PhaseResult.FAIL_AND_CONTINUE


@plan.testcase('Random')
def random_test(test, repeat_limit = 5):
    """Generate a random number between 1 and 10. If number is 8, 9, or 10 it is a PASS. If not repeat"""
    val = random.randint(1, 10)
    print (val)
    if val >= 8:
        return PhaseResult.CONTINUE
    else:
        return PhaseResult.REPEAT
        
@plan.testcase('Random 2')
def random_test(test):
   # """Generate a random number between 1 and 10. If number is 8, 9, or 10 it is a PASS. If not repeat"""
    val = random.randint(1, 10)
    print (val)
    if test.state["product"] == "A":        
        if val >= 8:
            return PhaseResult.CONTINUE
        else:
            return PhaseResult.FAIL_AND_CONTINUE
    elif test.state["product"] == "B":
        return PhaseResult.SKIP

    
if __name__ == '__main__':
    plan.run()

    


