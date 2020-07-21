from .base import UnboundPlug

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

    def __init__(self, addr, username=None, password=None, port=23):
        super().__init__()
        self.tn = None
        self.addr = addr
        self.port = port
        self.username = username
        self.password = password

    def open(self, _client=None):
        # _client allows to pass in a mock for testing
        self.logger.info("(Initiating Telnet connection at %s)", self.addr)
        self.logger.info("(addr={}:{}, user={!r}, password={!r})".format(
            self.addr, self.port, self.username, self.password))
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
            self.tn.write("\r\n")
            # If the Telnet object is not connected, an AttributeError is raised
        except AttributeError:
            return False
        else:
            return True

    @_telnet_client_connected
    def execute_command(self, command: str, timeout: float = 10, targets=None, assertexitcode:typing.Union[typing.List[int], int, None]=0):
        """Send a :obj:`command` and wait for it to execute.

        Args:
            command (str): The command to send. End of lines are automatically managed. For example execute_command('ls')
            will executed the ls command.
            timeout (float, optional): The timeout in second to wait for the command to finish executing. Defaults to 10.
            targets ([type], optional): [description]. Defaults to None.
            assertexitcode: Unless this is None, defines one or a list of exit codes that are expected. After the   command is executed, an :class:`SSHError` will be raised if the exit code is not as expected.

        Returns:
            str: output response from the Telnet client

        Raises:
            SSHTimeoutError:
                Raised when :obj:`timeout` is reached.
            SSHError:
                Raised when the exit code of the command is not in :obj:`assertexitcode` and :obj:`assertexitcode` is not None.
        """

        output = ""
        exit_code = None
        if command != "":
            self.logger.info("(Timeout %.1fs)" % (timeout))
            self.tn.write(command)
            self.logger.debug("> {!r}".format(command))

            try:
                output = self.read_some()
            except:
                raise TelnetError
            finally:
                self.tn.close()# Sends eof
        else:
            pass
        
        if assertexitcode is not None:
            assert_exit_code(exit_code, expected=assertexitcode)

        return output


def assert_exit_code(exit_code, expected):
    if not isinstance(expected, Sequence):
        expected = [expected]

    if exit_code not in expected:
        raise TelnetError(
            'Exit code {} not in expected list {}'.format(exit_code, expected))
