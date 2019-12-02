import os

import openhtf as htf
from openhtf.plugs.user_input import UserInput
from openhtf.util import conf

from spintop_openhtf import TestPlan

FORM_LAYOUT = {
    'schema':{
        'title': "First and Last Name",
        'type': "object",
        'required': ["firstname", "lastname"],
        'properties': {
            'firstname': {
                'type': "string", 
                'title': "First Name"
            },
            'lastname': {
                'type': "string", 
                'title': "Last Name"
            },
        }
    },
    'layout':[
        "firstname",
        "lastname"
    ]
}

class GreetPlug(UserInput):
    def prompt_tester_information(self):
        self.__response = self.prompt_form(FORM_LAYOUT)
        return self.__response
    
    def greet_tester(self):
        try:
            self.prompt('Hello {firstname} {lastname} !'.format(**self.__response))
        except AttributeError:
            raise Exception("Cannot greet tester before prompt_information")

""" Test Plan """

# This defines the name of the testbench.
plan = TestPlan('examples.hello_world')
plan.no_trigger()
# @plan.trigger('Hello-World')
@plan.plug(greet=GreetPlug)
def hello_world(test, greet):
    """Says Hello World !
    
# Hello World Test
    
Welcome to the **hello world** test.
    """
    response = greet.prompt_tester_information()
    test.dut_id = response['firstname']
    
# @plan.testcase('Greet the tester')
@plan.plug(greet=GreetPlug)
def greet_tester(test, greet):
    greet.greet_tester()

if __name__ == '__main__':
    conf.load(station_server_port='4444', capture_docstring=True)
    plan.run()
