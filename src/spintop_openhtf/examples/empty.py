import os

from openhtf.plugs.user_input import UserInput

from spintop_openhtf import TestPlan, conf
from spintop_openhtf.util.markdown import markdown

# This defines the name of the testbench.
plan = TestPlan('empty')

@plan.testcase('Nothing')
def test_something(test):
    pass

if __name__ == '__main__':
    plan.run()