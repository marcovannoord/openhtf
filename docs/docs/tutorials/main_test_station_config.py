# main.py
import os

import openhtf as htf
from openhtf.plugs.user_input import UserInput
from spintop_openhtf import TestPlan
from pprint import pprint
from time import sleep


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

conf.declare("serial")
conf.declare("ip_address")
conf.declare("test_constant")
conf.load_from_filename("config.yml")

@plan.trigger('Configuration')
@plan.plug(prompts=UserInput)
def trigger(test, prompts):
    """Displays the configuration form"""
    response = prompts.prompt_form(FORM_LAYOUT)
    test.dut_id = response['dutid']
    pprint (response)
    
    
@plan.testcase('Sleep')
def sleep_test(test):
    """Waits five seconds"""
    
    

    print ("Station ID is {}".format(conf.station_id))
    print ("Serial port is {}".format(conf.serial["comport"]))
    print ("IP address is {}".format(conf.ip_address))
    print ("Test constant is {}".format(conf.test_constant))
    
    sleep(5)
    
if __name__ == '__main__':
    plan.run()

    


