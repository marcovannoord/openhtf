from nute.service.base_service import *
import telnetlib


class TelnetServiceConfig():
    def __init__(self):
        self.addr = ""
        self.username = ""
        self.password = ""
        self.port = 21

class TelnetServiceRequest():
    def __init__(self):
        self.command = ""
        self.timeout = -1
        self.expect_kw = []

class TelnetServiceResponse():
    def __init__(self):
        self.output = ""
        self.kw_found = ""

TELNET_SERVICE_UUID = "telnet"

class TelnetService(Service):
    def __init__(self, url, **kwargs):
        Service.__init__(self, url, **kwargs)
        self.tn = None
        self.addr = None
        self.port = None
        self.username = None
        self.addr = None

    def service_config(self, config):
        self.addr = self.extract_param(config, "addr")
        self.username = self.extract_param(config, "username", default="")
        self.password = self.extract_param(config, "password", default="")
        self.port = self.extract_param(config, "port", default=23)
        self.logger.info("All parameters present")
        self.connect()

    def connect(self):
        self.logger.info("Initiating Telnet connection at %s", self.addr)
        try:
            self.tn = telnetlib.Telnet(self.addr, self.port)
        except Exception as e:
            raise ServiceError("Unable to connect to Telnet host: " + e.message)

    def is_connected(self):
        try:
            self.tn.write("\r\n")
		# If the Telnet object is not connected, an AttributeError is raised
        except AttributeError:
            return False
        else:
			return True

    def try_close(self):
        try:
            self.logger.info("Closing Telnet connection")
            self.tn.close()
        except:
            pass

    def telnet_client_connected(function):
        def check_connected(*args, **kwargs):
            _self = args[0]
            if not _self.is_connected():
                _self.logger.info("Connection is no longer alive")
                _self.connect()
            return function(*args, **kwargs)

        return check_connected

    def std_format(self, string):
        return string.strip().replace('\r', '')

    @telnet_client_connected
    def service_handle(self, request):
        command = self.extract_param(request, "command", default="")
        timeout = self.extract_param(request, "timeout", default=10)
        targets = self.extract_param(request, "targets", default=[])
        keeplines = self.extract_param(request, 'keeplines', default=0)

        if keeplines == 0:
            current_lines = self.tn.read_very_eager()
            if current_lines.strip():
                self.logger.debug(self.std_format(current_lines))

        output = ""
        kw_match = None
        index = -1
        if command != "":
            self.quick_log("Timeout is %.1fs. Expecting: %s . Sending command: %s" % (timeout, str(targets), command.strip()))

            command = command.decode('utf-8','ignore').encode("utf-8")
            self.tn.write(command)
            index, kw_match, output = self.tn.expect(targets,timeout)
            self.logger.debug(self.std_format(output))
        else:
            self.quick_log("No command specified")
        resp = TelnetServiceResponse()
        resp.output = output

        if len(targets) > 0:
            try:
                resp.kw_found = kw_match.group(0) #Raises error if no command specified
            except AttributeError:
                raise ServiceError('Unable to find keywords %s in %s' % (str(targets), self.std_format(output)))
        return resp

    def stream_poll(self, request):
        raise NotImplementedError

    def service_shutdown(self):
        self.try_close()

from _client_classes import NonBlockingCommunicationInterface, AuthenticatedServiceMixin, TCPServiceMixin, SCPIServiceMixin

class TelnetServiceClient(ServiceClient, NonBlockingCommunicationInterface, AuthenticatedServiceMixin, TCPServiceMixin, SCPIServiceMixin):

    def create_service(self, ipaddr=None, port=23, username=None, password=None, default_targets=[], eol='\n', addresseip=None, username_tn=None, password_tn=None):
        """
        addresseip, username_tn, password_tn for backward compatibility
        """
        if ipaddr is None and addresseip is not None: ipaddr = addresseip
        if username is None and username_tn is not None: username = username_tn
        if password is None and password_tn is not None: password = password_tn
        self.init(eol, default_targets)
        status, resp = self.new_service(uuid = TelnetService.__name__, addr=ipaddr, port=port,username=username, password = password)
        assert status < 400

    def init(self, eol='\n', default_targets=[]):
        self.eol = eol
        self.default_targets = default_targets

    def execute_command(self, command, timeout=10, targets=None, cmd=None, kw=[]):
        """
        cmd and kw for backward compatibility
        """
        if targets is None and len(kw) > 0: targets = kw
        if not command and cmd is not None: command = cmd

        if targets is None:
            targets = self.default_targets
        command = command.strip() + self.eol
        status, resp = self.service(command=command,timeout=timeout,targets=targets)
        return resp.output, resp.kw_found

    def execute_multiple_commands(self, commands, **kwargs):
        for command in commands:
            self.execute_command(command, **kwargs)
