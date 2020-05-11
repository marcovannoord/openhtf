# main.py
import os

import openhtf as htf
from openhtf.plugs.user_input import UserInput
from spintop_openhtf import TestPlan
from pprint import pprint


FORM_LAYOUT = {
    'schema':{
        'title': "Impedance",
        'type': "object",
        'required': ["impedance"],
        'properties': {
            'impedance': {
                'type': "string", 
                'title': "Measure Impedance on test point X\nEnter value in Ohms"
            },
        }
    },
    'layout':[
        "impedance"
    ]
}


""" Test Plan """

# This defines the name of the testbench.
plan = TestPlan('hello')

@plan.testcase('Hello-Test')
@plan.plug(prompts=UserInput)
def hello_world(test, prompts):
    """Displays the custom from defined above"""
    prompts.prompt_form(FORM_LAYOUT)
    
if __name__ == '__main__':
    plan.no_trigger()
    plan.run()
    



