from copy import copy

import openhtf as htf
from openhtf.plugs import user_input

import spintop

class TestPlan(object):
    def __init__(self):
        self._test_phases = []

    def testcase(self, name, tests=[]):
        def _note_fn(fn):
            fn = ensure_htf_phase(fn)
            fn.options.name = name # Use the testcase name
            self._test_phases.append(fn)
            return fn
        return _note_fn

    @property
    def phases(self):
        return copy(self._test_phases)

    def execute(self, callbacks=[]):
        test = spintop.Test(*self.phases, spintop_test_plan=self)
        test.add_output_callbacks(*callbacks)
        return test.execute(test_start=user_input.prompt_for_test_start())


def ensure_htf_phase(fn):
    if not hasattr(fn, 'options'):
        # Not a htf phase, decorate it so it becomes one.
        fn = htf.PhaseOptions()(fn) 
    return fn
