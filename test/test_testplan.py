
import pytest

from spintop.util import yaml_loader
from spintop.testplan import TestPlan, ElectricalAnalysisContext

def test_testplan_sequencing():
    plan = TestPlan()

    @plan.testcase('A')
    def fn1():
        pass

    @plan.testcase('B')
    def fn2():
        pass

    assert plan.phases == [fn1, fn2]


@pytest.fixture()
def fpga_yml_content():
    return yaml_loader.load_yml("""
nodes:
  - name: power
    nodes:
      - name: 5V
      - name: 3V
        implies: 
          - 5V
  - name: gps
    refdes: U33
    type: chip
    nodes:
      - name: uart
        testpoints:
          - GPS_UART
      - name: pps_out
        edges:
          - PPS_OUTPUT
    implies:
      - power.5V
  - name: uart_translator
    refdes: U231
    type: chip
    nodes:
      - name: uart
        edges:
          - GPS_UART
          - FPGA_UART
    implies:
      - power.5V
      - power.3V
  - name: fpga
    refdes: U4
    type: chip
    nodes:
      - name: uart
        edges:
          - FPGA_UART
      - name: pps_in
        edges:
          - PPS_OUTPUT
    implies:
      - power.3V
    """)
    
@pytest.fixture()
def fpga_yml_analysis(fpga_yml_content):
    analysis = ElectricalAnalysisContext()
    analysis.parse(fpga_yml_content)
    return analysis

def test_children_nodes(fpga_yml_content):
    
    
def test_nets_array():
    nets = [
        'A',
        'B',
        'C',
        'A, E' # Same Net
    ]

    nets = load_nets(nets)

    assert len(nets) == 4
    assert nets['A'] is nets['E'] # Assert same object
    
    assert 'A' in nets and 'E' in nets['A'].refs
    assert 'B' in nets
    assert 'C' in nets
    assert 'E' in nets and 'A' in nets['E'].refs

def test_nested_nets_array():
    nets = [
        'A',
        ['B', 'C']
    ]

    nets = load_nets(nets)
    assert len(nets) == 3
    for letter in 'ABC':
        assert letter in nets
    

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
        
def test_components_to_netlist():
    """
    Defined nets: A, B, C
    Defined Components: X, Y, Z
    """
    top_level = top_two_child_components(first_nets=['A', 'B'], second_nets=['C'])
    
    netlist = create_netlist_from_component(top_level)
    
    assert len(netlist) == 3
    for net in 'ABC':
        assert net in netlist
        
def top_two_child_components(top_nets=[], first_nets=[], second_nets=[]):
    return Component(name='X', nets=top_nets, components=[
        Component(name='Y', nets=first_nets),
        Component(name='Z', nets=second_nets),
    ])

def four_level_deep_components(nets_per_component=([],[],[],[])):
    return \
    Component(name='W', nets=nets_per_component[0], components=[
        Component(name='X', nets=nets_per_component[1], components=[
            Component(name='Y', nets=nets_per_component[2], components=[
                Component(name='Z', nets=nets_per_component[3], components=[])
            ])
        ])
    ])
        
def test_deep_components_to_netlist():
    """
    Defined nets: A, B, C, D
    Defined Components: W, X, Y, Z
    """
    top_level = four_level_deep_components(nets_per_component=(
        ['A'], ['B'], ['C'], ['D']
    ))
    
    netlist = create_netlist_from_component(top_level)
    
    assert len(netlist) == 4
    for net in 'ABCD':
        assert net in netlist
        
def test_netlist_links_components_nets():
    """
    Defined nets: A, B, C
    Defined Components: W, X
    """
    top_level = top_two_child_components(first_nets=['A,B'], second_nets=['B,C'])
    
    netlist = create_netlist_from_component(top_level)
    
    assert len(netlist) == 3
    assert netlist['A'] is netlist['B']
    assert netlist['B'] is netlist['C']
    
def test_netlist_links_components_nets():
    """
    Defined nets: A, B, C
    Defined Components: W, X
    """
    top_level = top_two_child_components(first_nets=['A,B'], second_nets=['B,C'])
    
    netlist = create_netlist_from_component(top_level)
    
    assert len(netlist) == 3
    assert netlist['A'] is netlist['B']
    assert netlist['B'] is netlist['C']

def test_components_fully_qual_nets():
    """ Components are named X, Y(first_nets), Z(second_nets) """
    top_level = top_two_child_components(first_nets=['A', 'B'], second_nets=['C'])
    
    net_qual_names = top_level.iter_fully_qualified_nets()
    
    assert set(net_qual_names) == {'X.Y.A', 'X.Y.B', 'X.Z.C'}
    
def test_analysis_netcomp():
    """ Components are named X, Y(first_nets), Z(second_nets) """
    top_level = top_two_child_components(first_nets=['A'], second_nets=['A'])
    
    analysis = CoverageAnalysis(top_level)
    keys = analysis.add_test(['X.Y.*'], 'test_a', allow_links_to=[])
    
    assert 'X.Y.A' in keys
    assert 'X.Z.A' not in keys
    
    keys = analysis.add_test(['X.Y.*'], 'test_b', allow_links_to=['*'])
    
    assert len(keys) == 2
    assert 'X.Y.A' in keys
    assert 'X.Z.A' in keys