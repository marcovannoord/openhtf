from copy import copy

import openhtf as htf

from openhtf.plugs import user_input
from openhtf.output.servers import station_server

from .. import (
    Test,
    # load_component_file,
    # CoverageAnalysis
)

class TestPlanError(Exception): pass

class TestPlan(object):
    def __init__(self):
        self._test_phases = []
        self._top_level_component = None
        self.coverage = None

    def testcase(self, name, tests=None, targets=[]):
        if tests and self._top_level_component is None:
            raise TestPlanError('The top level component must be defined using the define_top_level_component function of TestPlan in order to use tests or targets coverage parameters.')
        
        def _note_fn(fn):
            fn = ensure_htf_phase(fn)
            fn.options.name = name # Use the testcase name
            self._test_phases.append(fn)
            
            if tests:
                print(self.coverage.add_test(tests, name, allow_links_to=targets))
            
            return fn
        return _note_fn

    @property
    def phases(self):
        return copy(self._test_phases)

    def run(self, callbacks=[]):
        with station_server.StationServer() as server:
            while True:
                self.execute(callbacks + [server.publish_final_state])

    def execute(self, callbacks=[]):
        test = Test(*self.phases, spintop_test_plan=self)
        test.configure(failure_exceptions=(Exception,))
        test.add_output_callbacks(*callbacks)
        return test.execute(test_start=user_input.prompt_for_test_start())
    
    def define_top_level_component(self, _filename_or_component):
        if isinstance(_filename_or_component, str):
            component = load_component_file(_filename_or_component)
        else:
            component = _filename_or_component
        self._top_level_component = component
        self.coverage = CoverageAnalysis(self._top_level_component)

def ensure_htf_phase(fn):
    if not hasattr(fn, 'options'):
        # Not a htf phase, decorate it so it becomes one.
        fn = htf.PhaseOptions()(fn) 
    return fn
