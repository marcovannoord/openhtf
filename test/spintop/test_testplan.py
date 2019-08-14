from spintop import TestPlan, load_nets, load_nets_yml

def test_testplan_sequencing():
    plan = TestPlan()

    @plan.testcase('A')
    def fn1():
        pass

    @plan.testcase('B')
    def fn2():
        pass

    assert plan.phases == [fn1, fn2]

def test_nets_array():
    nets = [
        'A',
        'B',
        'C',
        'A,E' # Same Net
    ]

    nets = load_nets(nets)

    assert len(nets) == 4
    assert 'A' in nets and 'E' in nets['A'].refs
    assert 'B' in nets
    assert 'C' in nets
    assert 'E' in nets and 'A' in nets['E'].refs

def test_jinja2_expansion():
    net_yml_str = """
---
nets:
    {% for i in range(4) %}
    - A{{i}}
    {% endfor %}
    """

    nets = load_nets_yml(net_yml_str)

    assert len(nets) == 4
    for i in range(4):
        assert 'A%d' % i in nets
