.. _teststation-config-label:

## Test Station Configuration

!!! summary "Summary"
    This page illustrates the proposed method of implementation for the configuration of the test station on which the test bench runs

The test station configuration is the list of all parameters configuring the test station itself, that is parameters changing from station to station and test jig to test jig, such as ip adresses, com port, etc. 

### Definition

In the context of a test bench implementation on spintop-openhtf, the test station configuration is defined as a yaml file. As an example, the following yaml snippet defines the configuration of the serial port and ip address of a test bench.

```yaml
serial  :
 comport: "COM4"
 baudrate : "115200"
ip_address : "192.168.0.100"
test_constant: 4
```

Create a new .yml file, paste the above configurations in it and save it as *config.yml* in the same directory as your test bench *main.py* It will be imported in a test bench.


### Import from file
To load the configurations in the test logic, the openhth conf module must be imported. 

```python
from openhtf.util import conf
```

The configuration parameters used must then be defined. A description of the configuration can be added to the declaration.

```python
conf.declare("serial", 'A dict that contains two keys, "comport" and "baudrate"')
conf.declare("ip_address", 'The IP Address of the testbench')
conf.declare("test_constant", 'A test constant')
```

and the configuration file loaded.


```python
conf.load_from_filename("config.yml")
```
### Use configurations

Once loaded, the test station parameters can be accessed through the conf object. For example, to print soome of the configuration parameters, use the following in a test case:

```python
print ("Serial port is {}".format(conf.serial["comport"]))
print ("IP address is {}".format(conf.ip_address))
print ("Test constant is {}".format(conf.test_constant))
```

Add the above code excerpts to your latest test bench and run it.

The test will print the information in the console window as 
```bat
Serial port is COM4
IP address is 192.168.0.100
Test constant is 4
```

### Built-in station id parameter

Spintoo-openhtf uses a built-in parameter in the conf object that defines the test station id. The id used is the hostname of the PC on which the test bench runs. For example, printing the station ID of a PC whose hostname is "TutorialStation"

```python
print ("Station ID is {}".format(conf.station_id))
```

will result in 

```bat
Station ID is TutorialStation
```


### Tutorial source
```
# main.py
import os

import openhtf as htf
from openhtf.plugs.user_input import UserInput
from spintop_openhtf import TestPlan
from pprint import pprint
from time import sleep


from openhtf.util import conf


FORM_LAYOUT = {
    'schema':{
        'title': "Test configuration",
        'type': "object",
        'required': ["operator, uutid, product"],
        'properties': {
            'operator': {
                'type': "string", 
                'title': "Enter the operator name"
            },
            'dutid': {
                'type': "string", 
                'title': "Enter the device under test serial number"
            },
            'product': {
                'type': "string", 
                'title': "Enter the product name"
            }
        }
    },
    'layout':[
        "operator", "dutid", "product",
    ]
}

""" Test Plan """

# This defines the name of the testbench.
plan = TestPlan('hello')

conf.declare("serial")
conf.declare("ip_address")
conf.declare("test_constant")
conf.load_from_filename("config.yml")

@plan.trigger('Configuration')
@plan.plug(prompts=UserInput)
def trigger(test, prompts):
    """Displays the configuration form"""
    response = prompts.prompt_form(FORM_LAYOUT)
    test.dut_id = response['dutid']
    pprint (response)
    
    
@plan.testcase('Sleep')
def sleep_test(test):
    """Waits five seconds"""
    
    

    print ("Station ID is {}".format(conf.station_id))
    print ("Serial port is {}".format(conf.serial["comport"]))
    print ("IP address is {}".format(conf.ip_address))
    print ("Test constant is {}".format(conf.test_constant))
    
    sleep(5)
    
if __name__ == '__main__':
    plan.run()

```