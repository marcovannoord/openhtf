# Copyright 2018 Google Inc. All Rights Reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Simple OpenHTF test which launches the web GUI client."""

from datetime import datetime

import openhtf as htf
from openhtf.output.servers import station_server
from openhtf.output.web_gui import web_launcher
from openhtf.plugs import user_input
from openhtf.util import configuration, units, validators
import time
from openhtf.output.callbacks import json_factory
import os

CONF = configuration.CONF


@htf.measures(htf.Measurement("hello_world_measurement"))
def hello_world(test):
    test.logger.info("Hello World!")
    time.sleep(3)
    test.measurements.hello_world_measurement = "Hello Again!"


# Multiple measurements can be specified in a single decorator, using either of
# the above syntaxes.  Technically, these syntaxes can be mixed and matched, but
# as a matter of convention you should always use one or the other within a
# single decorator call.  You'll also note that you can stack multiple
# decorations on a single phase.  This is useful if you have a handful of simple
# measurements, and then one or two with more complex declarations (see below).
@htf.measures("first_measurement", "second_measurement")
@htf.measures(htf.Measurement("third"), htf.Measurement("fourth"))
def lots_of_measurements(test):
    test.measurements.first_measurement = "First!"
    # Measurements can also be access via indexing rather than attributes.
    test.measurements["second_measurement"] = "Second :("
    # This can be handy for iterating over measurements.
    for measurement in ("third", "fourth"):
        time.sleep(2)
        test.measurements[measurement] = measurement + " is the best!"


# @htf.plug(example=example_plugs.example_plug_configured)
# @htf.plug(frontend_aware=example_plugs.ExampleFrontendAwarePlug)
# def example_monitor(example, frontend_aware):
#   time.sleep(.2)
#   frontend_aware.increment()
#   return example.increment()


@htf.measures(
    htf.Measurement('widget_type').matches_regex(r'.*Widget$').doc(
        """This measurement tracks the type of widgets."""),
    htf.Measurement('widget_color').doc('Color of the widget'),
    htf.Measurement('widget_size').in_range(1, 4).doc('Size of widget'))
@htf.measures(
    'specified_as_args',
    docstring='Helpful docstring',
    units=units.HERTZ,
    validators=[validators.matches_regex('Measurement')])
# @htf.plug(example=example_plugs.example_plug_configured)
@htf.plug(prompts=user_input.UserInput)
def user_input_example(test, prompts):
  """A hello world test phase."""
  test.logger.info('Hello World!')
  test.measurements.widget_type = prompts.prompt(
      'What\'s the widget type? (Hint: try `MyWidget` to PASS)',
      text_input=True, timeout_s=20)
  if test.measurements.widget_type == 'raise':
    raise Exception()
  test.measurements.widget_color = 'Black'
  test.measurements.widget_size = 3
  test.measurements.specified_as_args = 'Measurement args specified directly'
#   test.logger.info('Plug value: %s', example.increment())

def attachments(test):
    test.attach("test_attachment", "This is test attachment data.".encode("utf-8"))
    test.attach_from_file(
        os.path.join(os.path.dirname(__file__), "example_attachment.txt")
    )
    time.sleep(2.2)
    test_attachment = test.get_attachment("test_attachment")
    assert test_attachment.data == b"This is test attachment data."

class ConsoleLogs():
    def __call__(self, record):
        for log_record in record.log_records:
            # Convert time stamp
            timestamp = datetime.fromtimestamp(log_record.timestamp_millis / 1000.0)
            timestamp_str = timestamp.strftime('%m/%d/%Y %H:%M:%S')
            print(f"{timestamp_str}\t{log_record.level}\t{log_record.message}")

def main():
    CONF.load(station_server_port="4444")
    with station_server.StationServer() as server:
        # web_launcher.launch("http://localhost:4444")
        for _ in range(5):
            test = htf.Test(hello_world, lots_of_measurements,user_input_example, attachments)
            test.add_output_callbacks(server.publish_final_state)
            test.add_output_callbacks(ConsoleLogs())
            test.add_output_callbacks(
                json_factory.OutputToJSON(
                    "./{dut_id}.{metadata[test_name]}.{start_time_millis}.json",
                    indent=4,
                )
            )
            test.execute(test_start=user_input.prompt_for_test_start())


if __name__ == "__main__":
    main()
