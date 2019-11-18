from spintop.util import yaml_loader
from spintop.testplan import TestPlan, ElectricalAnalysisContext

yml_raw= """
components:
  - name: power
    components:
      - name: 5V
      - name: 3V
        implies: 
          - power.5V
  - name: gps
    refdes: U33
    type: chip
    components:
      - name: uart
        testpoints:
          - GPS_UART
      - name: pps
    implies:
      - power.5V
  - name: uart_translator
    refdes: U231
    type: chip
    components:
      - name: uart
        testpoints:
          - GPS_UART
          - FPGA_UART
    implies:
      - power.5V
      - power.3V
  - name: fpga
    refdes: U4
    type: chip
    components:
      - name: core
        testpoints:
          - VERSION
      - name: uart
        testpoints:
          - FPGA_UART
      - name: pps_in
        implies: 
          - gps.pps
        testable: true
        
    implies:
      - power.3V
"""

def get_fig():
    yml_content = yaml_loader.load_yml(yml_raw)
    
    analysis = ElectricalAnalysisContext()
    analysis.parse(yml_content)
    g = analysis.build_graph()

    from spintop.util.graph import auto_graph_to_plotly_fig
    
    return auto_graph_to_plotly_fig(g, seed=98)

def run():
    fig = get_fig()
    fig.show()
    
if __name__ == '__main__':
    run()