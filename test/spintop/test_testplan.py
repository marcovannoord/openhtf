from spintop import TestPlan

def test_testplan_sequencing():
    plan = TestPlan()

    @plan.testcase('A')
    def fn1():
        pass

    @plan.testcase('B')
    def fn2():
        pass

    assert plan.phases == [fn1, fn2]

    