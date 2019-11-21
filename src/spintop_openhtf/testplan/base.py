from copy import copy

import openhtf as htf

from openhtf.plugs import user_input, BasePlug
from ..callbacks import station_server

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
        self.file_provider = station_server.TemporaryFileProvider()
        with station_server.StationServer(self.file_provider) as server:
            while True:
                try:
                    self.execute(callbacks + [server.publish_final_state])
                except KeyboardInterrupt:
                    break

    def execute(self, callbacks=[]):
        
        test = Test(*self.phases, spintop_test_plan=self)
        test.configure(failure_exceptions=(Exception,))
        test.add_output_callbacks(*callbacks)
        
        return test.execute(test_start=self._test_start(file_provider=self.file_provider))
    
    def create_plug(self):
        class _SelfReferingPlug(BasePlug):
            def __new__(cls):
                return self
        
        return _SelfReferingPlug
    
    def spintop_plug(self, fn):
        return htf.plugs.plug(spintop=self.create_plug())(fn)
    
    def _test_start(self, message='Enter a DUT ID in order to start the test.',
            validator=lambda sn: sn, **state):
        
        @htf.plugs.plug(prompts=user_input.UserInput)
        def trigger_phase(test, prompts):
            """Test start trigger that prompts the user for a DUT ID."""
            test.state.update(state)
                
            dut_id = prompts.prompt(
                message, text_input=True)
            test.test_record.dut_id = validator(dut_id)
        
        return trigger_phase
    
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
