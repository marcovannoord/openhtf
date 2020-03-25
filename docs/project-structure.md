# Project Structure

Altough Spintop-OpenHTF allows great flexibility in usage, certain basic principles should be followed in order to promote re-usability and maintainability of a testbench.

## Testbench Areas

### Configuration Management

The configuration of a testbench refers to all configuration values related to the deployment of the testbench to a specific test PC. These configuration values are stored in the OpenHTF conf module (`openhtf.util.conf`). Spintop-OpenHTF respects the OpenHTF convention:

> As a matter of convention, OpenHTF configuration files should contain values
which are specific to an individual station (not station type).  This is
intended to provide a means to decouple deployment of test code from
station-specific configuration or calibration.

> Examples of the types of values commonly found in the configuration are
physical port names, IP addresses, calibrated light/sound levels, etc.
**Configuration values should not be used to determine test flow, or to control
debug output.**

Therefore, configuration values declared using `conf.declare` should not affect test flow and only relate to the values specific to the local test PC, such as a COM port name or IP adresses.

#### Best Practices

Store the testbench configuration in a yaml file and load it using `conf.load_from_filename`. If you wish to version control the testbench-specific configuration file, you can use the hostname as the filename:

```python

# project structure:
# main.py (this file)
# configs/
#   PC1.yml
#   PC2.yml

import os
import socket
from spintop_openhtf import TestPlan, conf

plan = TestPlan()

# Load the test cases and declare the conf values (...)

if __name__ == '__main__':
    # Load the file configs/{hostname}.yml
    conf.load_from_filename(
        os.path.join('configs', '{}.yml'.format(socket.gethostname()))
    )
    plan.run()

```

### Test Flow Configuration Management

Although the configuration should not affect the test flow, it is good practices to parametrize the test sequences using constants or factories to build the test. For example, a test that can be executed accross a range of frequencies should be parametrizable using that range. 

However, changing that range should imply a completely new commit and a new testbench version, in opposition to, say, a COM port name in the testbench configuration. The COM port name needs to be changed during deployment, but not the frequency range.

#### Best Practices

Store the test flow configuration in a python file named `config.py` with parametric constants inside a *class*:

```python

# project structure:
# main.py 
# config.py (this file)
class Config():
    FREQUENCY_RANGE = [700, 750, 780, 800, 820, 850, 900]
# (...)

```

In your main, create a new instance of that (default) config and pass it as argument to any test factory that requires it. By creating an object instead of importing constants, it is easier to run a non-default configuration of your test and even to run unit tests by injecting a custom configuration.

```python
#main.py

from config import Config

config = Config()

# (use config object)
```

### Criteria Management

Criteria are a specific case of test flow configuration. Usual engineering practices separate the modification of the test sequences (and its configuration) from the modification of the acceptance criteria, the later being expected to be adjusted once production begins. 

#### Best Practices

Isolate all criteria in one file using *criteria factories* to easily identify changes to criteria -vs- changes to the test flow.

```python
# project structure:
# main.py 
# criteria.py (this file)

from spintop_openhtf import Measurement

def frequency_measures_factory(frequency_range):
    measure_name_format = 'measure_freq_{freq}'
    # No validators.
    # To add validators to a frequency range like that, a lookup function 
    # or a linear function could be sampled.
    return [Measurement(measure_name_format.format(freq=freq)) for freq in frequency_range]

```

### Test Sequences

The sequencing of your test is the core of your testbench. It is important to separate the test phases from the actual business logic in order for you to be able to re-use that business logic in another context than Spintop-OpenHTF.

#### Best Practices

Create *test factories* that create either test sequences or test plans based on the passed arguments.

```python
# project structure:
# main.py (this file)
# config.py (see configuration best practices)
# criteria.py (see criteria best practices)
# logic/ (or any other name that makes sense)
#   __init__.py
#   stuff_library.py
# sequences/
#   __init__.py
#   test_flow_1.py
#   (other test sequences)

from spintop_openhtf import TestPlan
from config import Config

from sequences.test_flow_1 import test_flow_1_factory

plan = TestPlan()
config = Config()

plan.append(
    test_flow_1_factory(config)
)

# (...)
```

```python
# sequences/test_flow_1.py
from spintop_openhtf import TestSequence

from logic import stuff_library
from criteria import frequency_measures_factory

def test_flow_1_factory(config):
    sequence = TestSequence('test-flow-1')

    # Call the measures factory that returns a list of measures 1:1 
    # with the frequencies.
    measures = frequency_measures_factory(config.FREQUENCY_RANGE)

    @sequence.testcase('A')
    @sequence.measures(*measures)
    def testA(test):
        # Keep the tests here as short as possible, and place 
        # the non-openhtf logic elsewhere to be reusable
        for freq, measure in zip(config.FREQUENCY_RANGE, measures):
            value = stuff_library.measure_frequency(freq)
            test.measurements[measure.name] = value

    return sequence
```
