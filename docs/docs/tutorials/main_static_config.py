# main.py
import os

import openhtf as htf
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
        'required': ["operator, uutid, product"],
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
    if test.state["product"] == "A":
        from static import ProductVersionA as ProductConfig
    elif test.state["product"] == "B":
        from static import ProductVersionB as ProductConfig   
    for x in range(SleepConfig.SLEEP_ITERATIONS):
        print ("Sleep iteration {} - sleep time {}".format(x, SleepConfig.SLEEP_TIME))
        sleep(SleepConfig.SLEEP_TIME)
    print ("I2C Address: {}".format(ProductConfig.TEMP_SENSOR_I2C_ADDR))
    
if __name__ == '__main__':
    plan.run()

    


