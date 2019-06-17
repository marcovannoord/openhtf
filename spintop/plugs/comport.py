import openhtf.plugs as plugs
from openhtf.util import conf

import serial

def define_comport_plug(comport_conf_name, comport_conf_baudrate=None):

    conf.declare(comport_conf_name, description='Declared comport accessor name')
    if comport_conf_baudrate is not None:
        conf.declare(comport_conf_baudrate, description='Declared comport baudrate')

    class ComportPlug(AbstractComportPlug, plugs.BasePlug):
        def __init__(self):
            if comport_conf_baudrate is None:
                baudrate = 115200
            else:
                baudrate = conf[comport_conf_baudrate]

            super(ComportPlug, self).__init__(conf[comport_conf_name], baudrate)

    return ComportPlug

class AbstractComportPlug(object):   # pylint: disable=no-init

    def __init__(self, comport, baudrate=115200):
        self.comport = comport
        self.baudrate = baudrate
        self._serial = None

    def tearDown(self):
        """Tear down the plug instance."""
        self.close()

    def close(self):
        if self._serial is not None and self._serial.is_open:
            self._serial.close()
            self._serial = None

    def open(self):
        self.close()
        self._serial = serial.Serial(self.comport, self.baudrate, timeout=1)

    def write(self, string):
        self._serial.write(string.encode('ascii'))

    def read(self):
        return self._serial.read(10).decode('ascii')
