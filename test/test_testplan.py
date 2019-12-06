import pytest
from spintop_openhtf import TestPlan

A_TEST_PLAN_NAME = 'test-plan'
A_TEST_NAME = 'Test1'

@pytest.fixture()
def test_plan():
    return TestPlan(A_TEST_PLAN_NAME, store_result=False)

def test_simple_testcase(test_plan):
    
    @test_plan.testcase(A_TEST_NAME)
    def test_1(test): # pylint: disable=unused-variable
        pass
    
    test_plan.configure()
    
    assert test_plan.trigger_phase is not None
    assert test_plan.phase_group.main and test_plan.phase_group.main[0].name == A_TEST_NAME
    
def test_no_trigger_and_run_with_gui(test_plan):
    test_plan.no_trigger()
    executed = []
    
    assert not executed
    
    @test_plan.testcase(A_TEST_NAME)
    def test_1(test): # pylint: disable=unused-variable
        executed.append(True)
    
    test_plan.run_once(launch_browser=False)
    
    assert executed
    
def test_custom_trigger(test_plan):
    executed = []
    
    assert not executed
    
    @test_plan.trigger('trigger')
    def test_trigger(test):
        executed.append(True)
    
    @test_plan.testcase(A_TEST_NAME)
    def test_1(test): # pylint: disable=unused-variable
        executed.append(True)
    
    test_plan.configure()
    test_plan.execute()
    
    assert len(executed) == 2
    
    
    
    
    
    