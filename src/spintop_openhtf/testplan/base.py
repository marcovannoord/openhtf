import os
import sys
import inspect
from copy import copy
from spintop.storage import SITE_DATA_DIR

import openhtf as htf

from openhtf.plugs import user_input, BasePlug
from ..callbacks import station_server

from .. import (
    Test,
    # load_component_file,
    # CoverageAnalysis
)

HISTORY_BASE_PATH = os.path.join(SITE_DATA_DIR, 'openhtf-history')

class TestPlanError(Exception): pass

class DecorativeTestNode(object):
    def __init__(self, name):
        self._setup_phases = []
        self._test_phases = []
        self._teardown_phases = []
        self.name = name
    
    def setup(self, name):
        return self._decorate_phase(name, self._setup_phases)
    
    def testcase(self, name, tests=None, targets=[]):
        # if tests and self._top_level_component is None:
        #     raise TestPlanError('The top level component must be defined using the define_top_level_component function of TestPlan in order to use tests or targets coverage parameters.')
        
        # def _note_fn(fn):
        #     phase = self._add_phase(fn, name, self._test_phases)
        #     # if tests:
        #     #     print(self.coverage.add_test(tests, name, allow_links_to=targets))
            
        #     return phase
        return self._decorate_phase(name, self._test_phases)
    
    def teardown(self, name):
        return self._decorate_phase(name, self._teardown_phases)
    
    def sub_group(self, name):
        group = DecorativeTestNode(name)
        self._test_phases.append(group)
        return group
    
    def _decorate_phase(self, name, array):
        def _note_fn(fn):
            phase = self._add_phase(fn, name, array)
            return phase
        return _note_fn
    
    def _add_phase(self, fn, name, array):
        phase = ensure_htf_phase(fn)
        phase.options.name = name
        # phase.extra_kwargs['testplan'] = self
        array.append(phase)
        return phase
        
    @property
    def phase_group(self):
        # Recursively get phase groups of sub phases if available, else the phase itself.
        _test_phases = [getattr(phase, 'phase_group', phase) for phase in self._test_phases]
        
        return htf.PhaseGroup(
            setup=self._setup_phases,
            main=_test_phases,
            teardown=self._teardown_phases,
            name=self.name
        )
    
class TestPlan(DecorativeTestNode):
    def __init__(self, name='testplan'):
        super(TestPlan, self).__init__(name=name)
        self._top_level_component = None
        self.coverage = None

    @property
    def history_path(self):
        path = os.path.join(HISTORY_BASE_PATH, self.name)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def run(self, callbacks=[]):
        self.file_provider = station_server.TemporaryFileProvider()
        with station_server.StationServer(self.file_provider) as server:
            self.configure(callbacks + [server.publish_final_state])
            while True:
                try:
                    self.execute()
                except KeyboardInterrupt:
                    break
    
    def configure(self, callbacks=[]):
        self.test = Test(self.phase_group, test_name=self.name, _code_info_after_file=__file__)
        self.test.configure(failure_exceptions=(user_input.SecondaryOptionOccured,))
        self.test.add_output_callbacks(*callbacks)
    
    def execute(self):
        return self.test.execute(test_start=self._test_start())
    
    def create_plug(self):
        class _SelfReferingPlug(BasePlug):
            def __new__(cls):
                return self
        
        return _SelfReferingPlug
    
    def spintop_plug(self, fn):
        return htf.plugs.plug(spintop=self.create_plug())(fn)
    
    def _test_start(self, message='Enter a DUT ID in order to start the test.',
            validator=lambda sn: sn, **state):
        
        @htf.PhaseOptions(timeout_s=None, requires_state=True)
        @htf.plugs.plug(prompts=user_input.UserInput)
        def trigger_phase(state, prompts):
            """Test start trigger that prompts the user for a DUT ID."""
            state.testplan = self
            dut_id = prompts.prompt(message, text_input=True)
            state.test_record.dut_id = validator(dut_id)
        
        trigger_phase.options.name = 'Simple Scan' # Use the testcase name
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
