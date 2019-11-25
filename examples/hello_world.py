""" This is the module-level summary of the hello_world test.
"""

import os
import time
import random

from spintop_openhtf import TestPlan
from spintop_openhtf.plugs.form_user_input import FormUserInput

import openhtf as htf

from openhtf.plugs.user_input import UserInput, PromptType
from openhtf.util import conf

""" Test Plan """

plan = TestPlan('examples.hello_world')
# plan.define_top_level_component('nets.yml')

HERE = os.path.abspath(os.path.dirname(__file__))

@plan.testcase('Hello-World')
@htf.plugs.plug(prompts=UserInput)
@htf.plugs.plug(prompt_form=FormUserInput)
@htf.PhaseOptions(requires_state=True)
def hello_world(state, prompts, prompt_form):
    """Says Hello World !
    
# Hello World Test
    
Welcome to the **hello world** test.
    """
    prompts.prompt('Cancel', prompt_type=PromptType.OKAY_CANCEL)
    prompts.prompt('PASS', prompt_type=PromptType.PASS_FAIL)
    state.logger.info('Hello World')
    prompt_form.prompt('Hello.', {})
    with state.testplan.file_provider.temp_file_url(os.path.join(HERE, 'spinsuite-2.png')) as image_url:
        url = '%s' % image_url
        prompts.prompt("""
# {url}

This is **Awesome**

Please tell me more.
<img src="{url}"></img>
                    """.format(url=url))


@plan.testcase('Hello-World-2')
@htf.plugs.plug(prompts=UserInput)
def hello_world(test, prompts):
    """Says Hello World 2 !"""
    test.logger.info('Hello World 2')

sub_group = plan.sub_group('sub-group')

@sub_group.testcase('sub Hello')
def hello_world(test):
    """Says Sub hello."""
    test.logger.info('Sub hello')

@sub_group.teardown('sub cleanup')
def hello_world(test):
    """Says Sub cleanup."""
    test.logger.info('Sub cleanup')
    
@plan.teardown('cleanup')
def cleanup(test):
    """Says Cleaned up."""
    test.logger.info('Cleaned up.')

if __name__ == '__main__':
    conf.load(station_server_port='4444', capture_docstring=True)
    plan.run()




