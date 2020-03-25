import paramiko
import socket
import time
from collections.abc import Sequence
from dataclasses import dataclass

from .base import UnboundPlug

class SSHError(Exception):
    pass

class SSHTimeoutError(SSHError):
    pass

@dataclass()
class SSHResponse():
    exit_code: str
    err_output: str
    std_output: str
    
    @property
    def output(self):
        return self.err_output + '\n' + self.std_output

def _ssh_client_connected(function):
    def check_connected(*args, **kwargs):
        _self = args[0]
        if not _self.is_connected():
            _self.logger.info("Connection is dead, reopening...")
            _self.open()
        return function(*args, **kwargs)

    return check_connected

class SSHInterface(UnboundPlug):
    def __init__(self, addr, username, password, create_timeout=3, port=22):
        super().__init__()
        self.ssh = None
        self.addr = addr
        self.username = username
        self.password = password
        self.create_timeout = create_timeout
        self.port = port

    def open(self, _client=None):
        self.logger.info("(Initiating SSH connection at %s)", self.addr)
        self.logger.info("(addr={}:{}, user={!r}, password={!r})".format(self.addr, self.port, self.username, self.password))
        try:
            # _client allows to pass in a mock for testing
            if _client is None: _client = paramiko.SSHClient()
            self.ssh = _client
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.addr, port=self.port, username=self.username, password=self.password, timeout=self.create_timeout)
            self.ssh.get_transport().set_keepalive(5) #Send keepalive packet every 5 seconds
        except Exception as e:
            raise SSHError("%s %s" % (str(e), e.message))

    
    def is_connected(self):
        if self.ssh is None or self.ssh.get_transport() is None:
            return False
        else:
            return self.ssh.get_transport().is_active()

    def close(self):
        self.logger.info("(Closing SSH connection)")
        self.ssh.close()

    @_ssh_client_connected
    def execute_command(self, command, timeout=60, stdin=[], get_pty=False, assertexitcode=0):
        output = ""
        err_output = ""
        exit_code = None
        if command != "":
            self.logger.info("(Timeout %.1fs, TTY=%s)" % (timeout, str(get_pty)))
            ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(command, get_pty=get_pty)
    
            self.logger.debug("> {!r}".format(command))
            for stdin_element in stdin:
                self.logger.debug("> {!r}".format(stdin_element))
                ssh_stdin.write('%s\n'%stdin_element)
                ssh_stdin.flush()

            ssh_stdin.close()# Sends eof

            try:
                self.wait_stdout_with_timeout(ssh_stdout, timeout)
                exit_code = ssh_stdout.channel.recv_exit_status()
            finally:
                ssh_stdout.channel.close()
                ssh_stderr.channel.close()
                output = ssh_stdout.read().decode('utf-8', 'ignore')
                err_output = ssh_stderr.read().decode('utf-8', 'ignore')


            self.logger.debug("(Exit code={}, Response:)\n{}".format(exit_code, output.strip()))
            if err_output:
                self.logger.debug("(STDERR:)\n{}".format(err_output.strip()))
        else:
            pass
        
        if assertexitcode is not None:
            assert_exit_code(exit_code, expected=assertexitcode)

        response = SSHResponse(exit_code=exit_code, err_output=err_output, std_output=output)

        return response
    
    def wait_stdout_with_timeout(self, stdout, timeout_seconds):
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            if stdout.channel.eof_received:
                break
            time.sleep(0)
        else:
            raise SSHTimeoutError(f'Client command timeout reached ({timeout_seconds}s)')



def assert_exit_code(exit_code, expected):
    if not isinstance(expected, Sequence):
        expected = [expected]
        
    if exit_code not in expected:
        raise SSHError('Exit code {} not in expected list {}'.format(exit_code, expected))
        

