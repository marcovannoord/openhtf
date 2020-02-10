import time

import threading
from queue import Queue, Empty
from asyncio import Protocol

class IOInterface(Protocol):
    """An interface to a read/write interface.
    
    Allows reading and writing. A background thread reads any data that comes in 
    and those lines can be accessed using the `next_line` function.
    
    """

    def __init__(self):
        self._line_buffer = ""
        self._read_lines = Queue()
        self._timeout_timer = None
        self._last_receive_time = None

        self.timeout = 0.5
        self.eol = "\n"

    def tearDown(self):
        """Tear down the plug instance."""
        self.close()

    def open(self, *args, **kwargs):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def write(self, string):
        """Write the string into the io interface."""
        raise NotImplementedError()

    def data_received(self, data):
        if self._timeout_timer is not None:
            self._timeout_timer.cancel()
        
        force_clear = False
        if self.check_receive_delta() and data is None and self._line_buffer:
            force_clear = True

        data_to_queue = None

        if not data:
            data = b''

        string = data.decode('utf8')
        if force_clear or string.endswith(self.eol) or (self._line_buffer + string).endswith(self.eol):
            data_to_queue = self._line_buffer + string
            self._line_buffer = ""
        else:
            self._line_buffer += string
        
        self._timeout_timer = threading.Timer(self.timeout, self.no_data_received)
        self._timeout_timer.start()

        if data_to_queue:
            strings_with_eol = data_to_queue.split(self.eol)
            # Last has no eol, all others do.
            for index, line in enumerate(strings_with_eol):
                if index < len(strings_with_eol) - 1:
                    line = line + self.eol

                if line:
                    self._read_lines.put(line)

    def no_data_received(self):
        return self.data_received(None)

    def check_receive_delta(self):
        if self._last_receive_time:
            delta = time.time() - self._last_receive_time
        else:
            delta = 0

        self._last_receive_time = time.time()

        return delta > self.timeout

    def keep_lines(self, lines_to_keep):
        """Clear all lines in the buffer except the last lines_to_keep lines."""
        if lines_to_keep == 0:
            self.clear_lines()
        else:
            current_lines = self._read_lines.qsize()
            print(current_lines)
            while current_lines > lines_to_keep:
                print(self.next_line())
                current_lines = current_lines - 1
        
    def clear_lines(self):
        """Clear all lines in the buffer."""
        self._read_lines.queue.clear()

    def next_line(self, timeout=10):
        """ Waits up to timeout seconds and return the next line available in the buffer.
        """
        try:
            return self._read_lines.get(timeout=timeout)
        except Empty:
            return None

    def eof_received(self):
        pass