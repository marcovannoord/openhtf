import os
import tornado

from tornado import web, iostream

from uuid import uuid4

from contextlib import contextmanager

from openhtf.output.servers.station_server import StationServer as HTFStationServer

WEB_GUI = os.path.join(os.path.dirname(__file__), 'web_gui')
STATIC_FILES_ROOT = os.path.join(WEB_GUI, 'dist')

TEMPFILES_PATH = '/tempfiles/'

class StationServer(HTFStationServer):
    def __init__(self, file_provider, *args, **kwargs):
        super(StationServer, self).__init__(*args, static_files_root=STATIC_FILES_ROOT, **kwargs)
        
        self.file_provider = file_provider
        self.file_provider.set_prefix(TEMPFILES_PATH)
        
        self.application.add_handlers(
            r".*",  # match any host
            [
                (
                    TEMPFILES_PATH + r"([^/]*)",
                    TemporaryFileHandler,
                    { 'file_provider': self.file_provider }
                ),
            ]
        )

class TemporaryFileProvider(object):
    def __init__(self):
        self.files = {}
        self.prefix = ''
    
    def set_prefix(self, prefix):
        self.prefix = prefix
    
    @contextmanager
    def temp_file_url(self, filename):
        subpath = self.prefix + str(uuid4())
        self.files[subpath] = filename
        try:
            yield subpath
        finally:
            del self.files[subpath]
            
        
class TemporaryFileHandler(tornado.web.RequestHandler):
    def initialize(self, file_provider):
        self.files = file_provider.files
    
    async def get(self, *args, **kwargs):
        print(self.request.path)
        try:
            filename = self.files[self.request.path]
        except KeyError:
            raise tornado.web.HTTPError(404)
        
        await self._write_file_chunks(filename)
        
    async def _write_file_chunks(self, filename):
        # chunk size to read
        chunk_size = 1024 * 1024 * 1 # 1 MiB

        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                try:
                    self.write(chunk) # write the cunk to response
                    await self.flush() # flush the current chunk to socket
                except iostream.StreamClosedError:
                    # this means the client has closed the connection
                    # so break the loop
                    break
                finally:
                    # deleting the chunk is very important because 
                    # if many clients are downloading files at the 
                    # same time, the chunks in memory will keep 
                    # increasing and will eat up the RAM
                    del chunk