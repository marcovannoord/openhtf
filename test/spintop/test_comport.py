import pytest
import time
import threading
import queue

from spintop.plugs.comport import ComportInterface

class FakeSerial(object):
    def __init__(self):
        self.to_read = ""
        self.is_open = True
        self.in_waiting = False
        self.echo = True
        self.was_read = threading.Event()

    def close(self):
        self.is_open = False

    def read(self, *args, **kwargs):
        if self.to_read:
            value = self.to_read
            self.to_read = ""
            self.in_waiting = False
            self.was_read.set()
            return value.encode('utf8')
        else:
            time.sleep(0.5)
            return None
    
    def write(self, string):
        if self.echo:
            self.in_waiting = True
            self.to_read += string.decode('utf8')

@pytest.fixture()
def fake_serial():
    fake_serial = FakeSerial()
    return fake_serial

@pytest.fixture()
def comport(fake_serial):
    # comport = ComportInterface('/dev/serial/by-id/usb-STMicroelectronics_STM32_Virtual_ComPort_in_FS_Mode_00000000050C-if00', 115200)
    comport = ComportInterface(None, None)
    comport.open(fake_serial)
    yield comport
    comport.close()


def test_receive_no_eol(fake_serial, comport):
    comport.write('Hello')
    line = comport.next_line(timeout=2)
    assert line == 'Hello'

def test_receive_immediate_eol(fake_serial, comport):
    fake_serial.was_read.clear()
    comport.write('Hello\n')
    # no wait now (only enough time for the thread to call read)
    fake_serial.was_read.wait()
    assert comport.next_line(timeout=0.1) == 'Hello\n'