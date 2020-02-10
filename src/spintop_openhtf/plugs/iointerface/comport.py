import openhtf.plugs as plugs
from openhtf.util import conf

import time

import serial
from serial.threaded import ReaderThread

from .base import IOInterface

class ComportInterface(IOInterface):
    """An interface to a comport.
    
    Allows reading and writing. A background thread reads any data that comes in 
    and those lines can be accessed using the `next_line` function.
    
    """

    def __init__(self, comport, baudrate=115200):
        super().__init__()
        self.comport = comport
        self.baudrate = baudrate

        self._serial = None
        self._reader = None

    def open(self, _serial=None):
        self.close()
        if not _serial:
            _serial = serial.Serial(self.comport, self.baudrate, timeout=self.timeout)
        self._serial = _serial
        self._reader = ReaderThread(self._serial, lambda: self)
        self._reader.start()

    def close(self):
        if self._reader is not None and self._serial.is_open:
            self._reader.close()
            self._reader = None

    def write(self, string):
        """Write the string into the comport."""
        return self._reader.write(string.encode('utf8'))

    def message_target(self, message, target, timeout=None, keeplines=0, poll_rate=0.05, **kwargs):
        to_raises = getattr(self, '_timeout_raises', True)
        to_raises = kwargs.pop('TO_raises', to_raises)
        contentstring = StringIO.StringIO()
        if isinstance(target, basestring):
            targets = self._parse_target(target)
        else:
            targets = target

        target_found = [None]
        def callback(content):
            if hasattr(content, 'read'):
                contentstring.write(content.read)
                for targetstr in targets:
                    if targetstr in content.read:
                        target_found[0] = targetstr
                        self.end_poll_early()

        with self as client:
            client.service(message=message, keeplines=keeplines)
            client.poll(callback, poll_rate, float(timeout))
        contentlog = contentstring.getvalue()
        contentstring.close()
        target_found = target_found[0]
        if target_found is None:
            if to_raises:
                raise ChannelServiceError('Message Target: timeout occured while waiting for %s' % str(targets))
            else:
                log_message = 'Message Target: timeout occured while waiting for %s' % str(targets)
        else:
            log_message='Message Target: Found %s' % target_found
        client.service(log_message=log_message)
        return contentlog



def declare_comport_plug(comport_conf_name, comport_conf_baudrate=None):
    """Creates a new plug class that will retrieve the comport name and baudrate (optionaly) from the openhtf conf.
    
    **Parameters:**
    
    * **comport_conf_name** - The name of the conf value that holds the comport name.
    * **comport_conf_baudrate** - (optional) The name of the conf value that holds the comport baudrate.
    
    **Returns:**
    
    A class that inherits from OpenHTF BasePlug and ComportInterface. This returned class can be used
    as a plug to feed into an OpenHTF test.
    
    """
    conf.declare(comport_conf_name, description='Declared comport accessor name')

    if comport_conf_baudrate is not None:
        conf.declare(comport_conf_baudrate, description='Declared comport baudrate')

    class ComportPlug(ComportInterface, plugs.BasePlug):
        def __init__(self):
            if comport_conf_baudrate is None:
                baudrate = 115200
            else:
                baudrate = conf[comport_conf_baudrate]

            super(ComportPlug, self).__init__(conf[comport_conf_name], baudrate)

    return ComportPlug
