import pytest

from spintop.util import yaml_loader
from spintop.coverage import new_analysis

@pytest.fixture()
def fpga_yml_content():
    return yaml_loader.load_yml("""
components:
  - name: power
    components:
      - name: 5V
      - name: 3V
        implies: 
          - root.power.5V
  - name: gps
    refdes: U33
    type: chip
    components:
      - name: uart
        testpoints:
          - GPS_UART
      - name: pps_out
        testpoints:
          - PPS_OUTPUT
    implies:
      - root.power.5V
  - name: uart_translator
    refdes: U231
    type: chip
    components:
      - name: uart
        testpoints:
          - GPS_UART
          - FPGA_UART
    implies:
      - root.power.5V
      - root.power.3V
  - name: fpga
    refdes: U4
    type: chip
    components:
      - name: uart
        testpoints:
          - FPGA_UART
      - name: pps_in
        testpoints:
          - PPS_OUTPUT
    implies:
      - root.power.3V

interfaces:
  - name: uart_gps_fpga
    type: UART
    endpoints:
      - gps.uart # GPS_UART_RX, GPS_UART_TX on GPS chip side
      - fpga.uart # FPGA_UART_RX, FPGA_UART_TX on FPGA side
    intermediate:
      - uart_translator.uart # Both low and high UART sides on translator
  - name: gps_pps
    type: GPS_PPS
    enpoints:
      - fpga.pps_in
      - gps.pps_out
    """)

def test_parse(fpga_yml_content):
    
    analysis = new_analysis.NodeTreeContext()
    analysis.parse(fpga_yml_content)
    g = analysis.build_graph()

    from spintop.util.graph import auto_graph_to_plotly_fig
    
    fig = auto_graph_to_plotly_fig(g, seed=98)
    fig.show()
    