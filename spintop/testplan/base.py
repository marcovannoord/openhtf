import openhtf as htf
from openhtf.plugs import user_input

from copy import copy

class TestPlan(object):
    def __init__(self):
        self._test_phases = []

    def testcase(self, name, tests=[]):
        def _note_fn(fn):
            fn.options.name = name # Use the testcase name
            self._test_phases.append(fn)
            return fn
        return _note_fn

    @property
    def phases(self):
        return copy(self._test_phases)

    def execute(self, callbacks=[]):
        test = htf.Test(*self.phases)
        test.add_output_callbacks(*callbacks)
        return test.execute(test_start=user_input.prompt_for_test_start())