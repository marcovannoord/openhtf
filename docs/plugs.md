# Plugs

## Introduction

Plugs are an OpenHTF concept. The OpenHTF team defines them as follow:

> The essence of an OpenHTF test is to interact with a DUT to exercise it in various ways and observe the result. Sometimes this is done by communicating directly with the DUT, and other times it's done by communicating with a piece of test equipment to which the DUT is attached in some way. A **plug** is a piece of code written to enable OpenHTF to interact with a particular type of hardware, whether that be a DUT itself or a piece of test equipment.

Technically, plugs are a Python class that is instanciated once per test and shared between test phases. They have a strong sense of *cleanup* that allows them to execute specific teardown actions regardless of the test outcome.

Altough OpenHTF references hardware directly, plugs are also used in various roles that are non-related to hardware, such as user input. Overall, a better explanation would be that they are used for resources that are shared by test cases:

- Plugs for test equipments
- Plugs for DUT interfacing, which can be subdivised in some cases:
    - COM Interface
    - SSH Interface
    - Etc.
- Plugs for user input
- Plugs for custom frontend interaction
- Plugs for sharing test context, such as calibration performed over multiple test cases

## Using Plugs

Using plugs in spintop-openhtf is pretty straightforward. We'll take the UserInput plug as example since it is used in pretty much all tests.

1. First, the plug must be imported.
    ```python
    from openhtf.plugs.user_input import UserInput
    ```

2. Then, on testcases that require this plug, the plug decorator must be used.

    ```python
    from openhtf.plugs.user_input import UserInput
    from spintop_openhtf import TestPlan

    plan = TestPlan('mytest')

    @plan.testcase('TEST1')
    @plan.plug(prompt=UserInput) # 'prompt' is user-defined
    def test_1(test, prompt): # prompt will contain an instance of UserInput
        ...
    
    ```

    The *class* of the plug is used as argument to the plug decorator. **This is important**. The executor will instantiate an instance of the class and use the same object across a test run. **On each new test, the plug will be re-instantiated.**

!!! warning
    You choose the name you want to give to the argument. The name must have a match in the function definition. For example, **the following would FAIL**:

    ```python

    # Will complain that 'prompt' is not an argument
    @plan.testcase('TEST1')
    @plan.plug(prompt=UserInput) 
    def test_1(test, user_input): # WRONG. No user_input argument exists
        ...

    ```


## Creating Plugs

Creating plugs is the basis of reusing interface functionnalities. As an example, we will create a plug that programs a test firmware with a simple copy to a virtual device, as you would do to flash newer ARM MBed-enabled devices.

### Base Structure

Every plug must inherit from `BasePlug`. Moreover, the `__init__` method must take no arguments.

```python

import shutil

from openhtf.plugs import BasePlug

class MBedProgrammer(BasePlug):
    def program_firmware(self, firmware_file, target_folder):
        shutil.copy(firmware_file, target_folder)


```

### Making it useful

As it stands, the programmer we created is useless compared to a simple function file. The caller must know both the firmware file and the target folder.

If we have a certain device, we usually have a specific target folder we will always use throughout the test. We therefore want to be able to specify, as configuration, the target folder. And, if we have multiple target within the same test, we want to have different configuration names.

Since OpenHTF configuration is global, we need to declare different conf variables when our test plan is imported. Instead of having a simple class definition, we will have a factory function that declares both a class and the associated configuration variables. This will allow us to:

- Add configuration values to our plug
- Use the same plug multiple times within the same test
- Use multiple instances of the plug within the same test
- Let the plug user decide the configuration value names he wishes to use

### Reusable Structure with Configuration

The standard term to declare configuration values is `declare`. We will reuse that term when naming our plug factory, just as spintop-openhtf builtin plugs use it.

```python

import shutil

from openhtf.plugs import BasePlug
from openhtf.util import conf

def declare_mbed_programmer(target_folder_conf_name, programmer_name='default'):
    conf.declare(target_folder_conf_name, description='MBedProgrammer "%s" target folder for firmware programming.' % programmer_name)

    # Note that the class is defined dynamically INSIDE the function call.
    # This gives us access to the factory arguments, such as
    # target_folder_conf_name
    class MBedProgrammer(BasePlug):
        def program_firmware(self, firmware_file, target_folder=None):
            if target_folder is None:
                target_folder = conf[target_folder_conf_name]
            mbed_program_firmware(firmware_file, target_folder)
    
    # Return the CLASS that is newly declared
    return MBedProgrammer

def mbed_program_firmware(firmware_file, target_folder):
    shutil.copy(firmware_file, target_folder)


```

### Trying it out

Our plug is used with the `declare_mbed_programmer` function. Let's create the bare minimum test plan that uses it:

```python
from spintop_openhtf import TestPlan

from openhtf.util import conf

# Say our plug is in plugs.py besides this file.
from plugs import declare_mbed_programmer

""" Test Plan """

plan = TestPlan('examples.program_firmware')

conf.declare('programmer_firmware_file', description='The firmware file to program.')

MyProgrammer = declare_mbed_programmer('programmer_target_folder')

@plan.testcase('Program')
@plan.plug(programmer=MyProgrammer)
def hello_world(test, programmer):
    """Programs the firmware file"""
    programmer.program_firmware(conf['programmer_firmware_file'])

if __name__ == '__main__':
    plan.run()

```

The configuration is now *declared* but no values are *defined* yet for `programmer_firmware_file` and `programmer_target_folder`. We can load it in code using `conf.load_from_file`:

```yaml
# myconfig.yml
---
programmer_firmware_file: 'myfile.elf' 
programmer_target_folder: '/dev/X/Y'

```

```python

# ...

if __name__ == '__main__':
    with open('myconfig.yml') as myconfig:
        conf.load_from_file(myconfig)
    plan.run()

```


!!! warning
    The configuration values can also be loaded in-code, but is considered best practices *not* to do so:

    ```python

    # ...

    if __name__ == '__main__':
        conf.load(
            firmware_file='myfile.elf', 
            programmer_target_folder='/dev/X/Y'
        )
        plan.run()

    ```

### Auto Documentation

Did you notice the different descriptions we gave to `conf.declare` ? These can be accessed by running the test with the `--config-help` option.

!!! summary "Output"
    ```console
    $ python program_firmware.py --config-help

    ...

    programmer_firmware_file
    ------------------------
    The firmware file to program.


    programmer_target_folder
    ------------------------
    MBedProgrammer "default" target folder for firmware programming.

    ...
    ```

## Built-in Plugs

### Comport

Reading and writing data to a comport is a frequent occurance in many testbenches. Spintop-OpenHTF includes a Comport plug that simplifies these operations.

#### Standalone Interface

```python

from spintop_openhtf.plugs import comport

interface = comport.ComportInterface('COM5')
# Do something with interface

```

#### OpenHTF Test Plug

```python

from spintop_openhtf import TestPlan
from spintop_openhtf.plugs import comport
from openhtf.util import conf

# Define a new plug that will get the comport name (COMX, /dev/tty, etc.) from a config value named my_board_comport
MyBoardComport = comport.declare_comport_plug('my_board_comport')

# Load the config value. Usually done with a config file.
conf.load(my_board_comport='COM5')
# (config file)
conf.load_from_filename('my-config.yml')

# This defines the name of the testbench.
plan = TestPlan('examples.comport')

@plan.testcase('Interface')
@plan.plug(interface=MyBoardComport)
def interface_test(test, interface):
    # Do something with interface

```



