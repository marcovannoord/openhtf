# main.py
from openhtf.plugs.user_input import UserInput
from spintop_openhtf import TestPlan

""" Test Plan """

# This defines the name of the testbench.
plan = TestPlan('hello')


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

@plan.testcase('userinput-Test')
@plan.plug(prompts=UserInput)
def userinput(test, prompts):
    """Displays the custom from defined above"""
    prompts.prompt_form(FORM_LAYOUT)


@plan.testcase('Hello-Test')
@plan.plug(prompts=UserInput)
def hello_world(test, prompts):
    prompts.prompt('Hello Operator!')
    test.dut_id = 'hello' # Manually set the DUT Id to same value every test

if __name__ == '__main__':
    plan.no_trigger()
    plan.run()