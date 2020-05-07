.. _teststation-config-label:

## Test Station Configuration

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


### Load Configuration from File

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
### Use Configuration

Once loaded and declared, the test station parameters can be accessed through the conf object. For example, to print soome of the configuration parameters, use the following in a test case:

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

Spintop-openhtf uses a built-in parameter in the conf object that defines the test station id. The id used is the hostname of the PC on which the test bench runs. For example, printing the station ID of a PC whose hostname is "TutorialStation"

```python
print ("Station ID is {}".format(conf.station_id))
```

will result in 

```bat
Station ID is TutorialStation
```

:download:`Tutorial source <../tutorials/main_test_station_config.py>`

:download:`Configuration file <../tutorials/config.yml>`
