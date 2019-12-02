
from openhtf.core.test_record import Outcome
from openhtf.output.callbacks.json_factory import OutputToJSON


class LocalStorageOutput(OutputToJSON):
    def __call__(self, test_record):
        if test_record.is_started():
            return super(LocalStorageOutput, self).__call__(test_record)