import os
import sys
import inspect
import datetime
from copy import copy
from contextlib import contextmanager

import openhtf as htf

from openhtf.util import conf
from openhtf.plugs import user_input, BasePlug

import webbrowser

from ..storage import SITE_DATA_DIR
from ..callbacks import station_server
from ..callbacks.local_storage import LocalStorageOutput

from .. import (
    Test,
    # load_component_file,
    # CoverageAnalysis
)

HISTORY_BASE_PATH = os.path.join(SITE_DATA_DIR, 'openhtf-history')

DEFAULT = object()

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
    
    def plug(self, *args, **kwargs):
        """Helper method: shortcut to htf.plugs.plug(...)"""
        return htf.plugs.plug(*args, **kwargs)
    
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
    def __init__(self, name='testplan', store_result=True):
        super(TestPlan, self).__init__(name=name)
        
        self._top_level_component = None
        self.coverage = None
        self.file_provider = station_server.TemporaryFileProvider()
        self.callbacks = []
        
        # Array but must contain only one phase.
        # Array is for compatibility with self._decorate_phase function of parent class.
        self._trigger_phases = []
        self._no_trigger = False
        
        if store_result:
            self.add_callbacks(LocalStorageOutput(self._local_storage_filename_pattern, indent=4))

    def _local_storage_filename_pattern(self, **test_record):
        folder = '{metadata[test_name]}'.format(**test_record)
        start_time_datetime = datetime.datetime.utcfromtimestamp(test_record['start_time_millis']/1000.0)
        start_time = start_time_datetime.strftime(r"%Y_%m_%d_%H%M%S_%f")
        filename = '{dut_id}_{start_time}_{outcome}.json'.format(start_time=start_time, **test_record)
        return os.path.join(HISTORY_BASE_PATH, folder, filename)
    
    @property
    def history_path(self):
        path = os.path.join(HISTORY_BASE_PATH, self.name)
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    
    @property
    def trigger_phase(self):
        return self._trigger_phases[0] if self._trigger_phases else None
        
    def freeze_trigger_phase(self):
        if self._trigger_phases:
            pass # OK
        elif self._no_trigger:
            pass # Don't create default trigger
        else:
            self._create_default_trigger()
    
    def trigger(self, name):
        if self.trigger_phase:
            raise TestPlanError('There can only be one @trigger function.')
        
        return self._decorate_phase(name, self._trigger_phases)

    def no_trigger(self):
        self._no_trigger = True

    def run(self, launch_browser=True, **execute_kwargs):
        with self.station_server_context(launch_browser):
            while True:
                try:
                    self.execute(**execute_kwargs)
                except KeyboardInterrupt:
                    break
    
    def run_once(self, launch_browser=True, **execute_kwargs):
        with self.station_server_context(launch_browser):
            self.execute(**execute_kwargs)
    
    @contextmanager
    def station_server_context(self, launch_browser=True):
        with station_server.StationServer(self.file_provider) as server:
            self.add_callbacks(server.publish_final_state)
            self.configure()
            self.assert_runnable() # Check before launching browser
            
            if launch_browser and conf['station_server_port']:
                webbrowser.open('http://localhost:%s' % conf['station_server_port'])
            
            yield
    
    
    def configure(self):
        self.test = Test(self.phase_group, test_name=self.name, _code_info_after_file=__file__)
        self.test.configure(failure_exceptions=(user_input.SecondaryOptionOccured,))
        self.test.add_output_callbacks(*self.callbacks)
        
        self.freeze_trigger_phase()
        
    def add_callbacks(self, *callbacks):
        self.callbacks += callbacks
    
    def assert_runnable(self):
        if not self.is_runnable:
            # No phases ! Abort now.
            raise RuntimeError('Test is empty, aborting.')
    
    @property
    def is_runnable(self):
        phases = self._test_phases + self._trigger_phases
        return bool(phases)
    
    def execute(self):
        """ Execute the configured test using the test_start function as a trigger.
        """
        self.assert_runnable()
        return self.test.execute(test_start=self.trigger_phase)
    
    def create_plug(self):
        class _SelfReferingPlug(BasePlug):
            def __new__(cls):
                return self
        
        return _SelfReferingPlug
    
    def spintop_plug(self, fn):
        return htf.plugs.plug(spintop=self.create_plug())(fn)
    
    def _create_default_trigger(self, message='Enter a DUT ID in order to start the test.',
            validator=lambda sn: sn, **state):
        
        @self.trigger('Simple Scan')
        @htf.PhaseOptions(timeout_s=None, requires_state=True)
        @htf.plugs.plug(prompts=user_input.UserInput)
        def trigger_phase(state, prompts):
            """Test start trigger that prompts the user for a DUT ID."""
            dut_id = prompts.prompt(message, text_input=True)
            state.test_record.dut_id = validator(dut_id)
            
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
