""" This is the module-level summary of the hello_world test.
"""

import os
import time
import random

from spintop_openhtf import TestPlan

import openhtf as htf

from openhtf.plugs.user_input import UserInput
from openhtf.util import conf

""" Test Plan """

plan = TestPlan()
# plan.define_top_level_component('nets.yml')

HERE = os.path.abspath(os.path.dirname(__file__))

@plan.testcase('Hello-World')
@htf.plugs.plug(prompts=UserInput)
def hello_world(test, prompts):
    """ Find the bluetooth device """
    test.logger.info('Hello World')
    with plan.file_provider.temp_file_url(os.path.join(HERE, 'spinsuite-2.png')) as image_url:
        url = '%s' % image_url
        prompts.prompt("""
<div>
    <h1>{url}</h1>
    <img src="{url}"></img>
</div>
                    """.format(url=url))

@plan.testcase('Hello-World-2')
@htf.plugs.plug(prompts=UserInput)
def hello_world(test, prompts):
    """ Find the bluetooth device """
    test.logger.info('Hello World 2')


if __name__ == '__main__':
    conf.load(station_server_port='4444', capture_source=True)
    plan.run()




