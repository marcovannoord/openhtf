from .base import UnboundPlug

import typing
from functools import wraps
from collections.abc import Sequence

import telnetlib


class TelnetError(Exception):
    pass


def _telnet_client_connected(function):
    @wraps(function)
    def check_connected(*args, **kwargs):
        _self = args[0]
        if not _self.is_connected():
            _self.logger.info("Connection is no longer alive")
            _self.open()
        return function(*args, **kwargs)

    return check_connected


class TelnetInterface(UnboundPlug):

    def __init__(self, addr, port=4343):
        super().__init__()
        self.tn = None
        self.addr = addr
        self.port = port

    def open(self, _client=None):
        # _client allows to pass in a mock for testing
        self.logger.info("(Initiating Telnet connection at %s)", self.addr)
        self.logger.info("(addr={}:{})".format(self.addr, self.port))
        try:
            if _client is None:
                _client = telnetlib.Telnet(self.addr, self.port)
            self.tn = _client
            self.tn.open(self.addr, port=self.port)
        except Exception as e:
            raise TelnetError("Unable to connect to Telnet host: " + str(e))

    def close(self):
        try:
            self.logger.info("Closing Telnet connection")
            self.tn.close()
        except:
            pass

    def is_connected(self):
        try:
            self.tn.write("\r\n".encode())
            # If the Telnet object is not connected, an AttributeError is raised
        except AttributeError:
            return False
        else:
            return True

    @_telnet_client_connected
    def execute_command(self, command: str, timeout: float = 10, targets=None):
        """Send a :obj:`command` and wait for it to execute.

        Args:
            command (str): The command to send. End of lines are automatically managed. For example execute_command('ls')
            will executed the ls command.
            timeout (float, optional): The timeout in second to wait for the command to finish executing. Defaults to 10.
            targets ([type], optional): [description]. Defaults to None.

        Returns:
            str: output response from the Telnet client

        Raises:
            TelnetError:
                Raised when reading the output goes wrong.
        """

        output = ""
        if command != "":
            from time import sleep
            self.logger.info("(Timeout %.1fs)" % (timeout))
            self.tn.write((command).encode() + b"\r\n")
            self.logger.debug("> {!r}".format(command))

            try:
                output = self.tn.read_very_eager()
                output = output.decode()
            except Exception as e:
                raise TelnetError(e)
        else:
            pass

        return output
