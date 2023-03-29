# main.py
from time import sleep
from openhtf.plugs.user_input import UserInput
from pprint import pprint
from spintop_openhtf import TestPlan, TestSequence

""" Test Plan """

# This defines the name of the testbench.
plan = TestPlan('PSU Plan')
hello_world_plan = TestPlan('Hello World Plan')


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

TEST_PICKER_LAYOUT = {
    'schema':{
        'title': "Select which tests to run",
        'type': "object",
        'required': ["test_name"],
        'properties': {
            'test_name': {
                'type': "string",
                'title': "Test name"
            },
        }
    },
    'layout':[
        "remarks",
        {
            "key": "test_name",
            "type": "radiobuttons",
            "titleMap": [
                { "value": "psu_test", "name": "PSU Test" },
                { "value": "input_test", "name": "input test" }
            ]
        }
    ]
}

sequence = TestSequence('DC state pre-tests')
sub_sequence = sequence.sub_sequence("DC Temperature tests")

@sequence.testcase('Sleep Test 1')
def sleep_test_1(test):
    """Waits 2 seconds"""
    sleep(2)

@sub_sequence.testcase('Temperature UTP test')
def temp_UTP_test(test):
    """Waits 2 seconds"""
    sleep(2)

@sub_sequence.testcase('Temperature OTP test')
def temp_OTP_test(test):
    """Waits 2 seconds"""
    sleep(2)


@sequence.testcase('DC Voltage regulation setpoint/readback')
def setpoint_readback_test(test):
    """Waits 2 seconds"""
    sleep(2)


# @plan.testcase('userinput-Test')
# @plan.plug(prompts=UserInput)
# def test_picker(test, prompts):
#     """Displays the custom from defined above"""
#     response = prompts.prompt_form(TEST_PICKER_LAYOUT)
#     picked_test = response["test_name"]
#     if picked_test == "psu_test":
#         plan.append(sequence)


# @plan.testcase('Hello-Test')
# @plan.plug(prompts=UserInput)
# def hello_world(test, prompts):
#     prompts.prompt('Hello Operator!')
#     test.dut_id = 'hello' # Manually set the DUT Id to same value every test



@plan.trigger('Configuration', requires_state=True)
@plan.plug(prompts=UserInput)
def trigger(test, prompts):
    """Displays the configuration form"""
    response = prompts.prompt_form(TEST_PICKER_LAYOUT)
    # test.dut_id = response['dutid']
    # test.state["operator"] = response['operator']
    # test.state["test_name"] = response['test_name']
    if response['test_name'] == "psu_test":
        plan.append(sequence)
        pprint("adding extra step")
    else:
        pprint("not adding extra step")
    pprint (response)

if __name__ == '__main__':
    plan.no_trigger()
    plan.append(sequence)
    plan.run(launch_browser=False)

    # plan.append(sequence)
