from copy import copy

class TestPlan(object):
    def __init__(self):
        self._test_phases = []

    def testcase(self, name, tests=[]):
        def _note_fn(fn):
            self._test_phases.append(fn)
            return fn
        return _note_fn

    @property
    def phases(self):
        return copy(self._test_phases)