import os

from openhtf.output.servers.station_server import StationServer as HTFStationServer

WEB_GUI = os.path.join(os.path.dirname(__file__), 'web_gui')
STATIC_FILES_ROOT = os.path.join(WEB_GUI, 'dist')


class StationServer(HTFStationServer):
    def __init__(self, *args, **kwargs):
        super(StationServer, self).__init__(*args, static_files_root=STATIC_FILES_ROOT, **kwargs)