# main.py
import os

import openhtf as htf
from openhtf.plugs.user_input import UserInput
from spintop_openhtf import TestPlan, TestSequence
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



sequence = TestSequence('Sleep Sequence')

sub_seq = sequence.sub_sequence('Sleep Sub Sequence 1')

@sub_seq.setup('Sub-sequence Setup')
def sub_setup(test):
    """Says Sub setup."""
    test.logger.info('Sub setup')

@sub_seq.testcase('Sleep Test 1A')
def sleep_test_1A(test):
    """Waits five seconds"""
    sleep(5)
    
@sub_seq.testcase('Sleep Test 1B')
def sleep_test_1B(test):
    """Waits five seconds"""
    sleep(5)

@sub_seq.teardown('Sub-sequence Cleanup')
def sub_cleanup(test):
    """Says Sub cleanup."""
    test.logger.info('Sub cleanup')
    
sub_seq = sequence.sub_sequence('Sleep Sub Sequence 2')
@sub_seq.testcase('Sleep Test 2')
def sleep_test_3(test):
    """Waits five seconds"""
    sleep(5)

plan.append(sequence)    

if __name__ == '__main__':
    plan.run()

    


