# Project Outline for OS4000-T Compass Test
Author: Matt Casari
Date: September 7, 2017

## Overview
The OS4000-T Compass Test is being designed to quantitatively assess the status
of each of the 250 OS4000-T units recently purchased by GTMBA, EDD and OCS groups
at PMEL.  By testing within a year of delivery, any defects can be returned to the
vendor under warranty for repair or replacement.


## Limited Number of Modules for Testing
To prevent overhandling of the compass modules, an initial quantity of three (3)
compass modules shall be provided for early testing provided from EDD stock. Only
when the test system has been signed off as stable shall testing of GTMBA, OCS
and the remainder of the EDD compass modules be allowed.

## Scope of Project
The test of the OS4000-T shall be a combination of both electrical test, connectivity test and performance accuracy test.

For electrical test, an input current measurement shall be made while the device is powered with a 3.3v source.  

For connectivity testing, the OS4000-T must receive configuration updates, and transmit both requested configurations as well as stream compass data.

The performance accuracy data shall test the repeatibility of the OS4000-T after it has been calibrated.


### Automated Read from OS4000-T
The test program must be able to read the OS4000-T.  Specifically:
1. Dump all parameters (<Esc>&) and parse each variable.
1. Read and parse the data string (after the output format has been set)

### Automated Write to OS4000-T
The test program must be capable of setting the following parameters when connected to the OS4000-T:

| Name | Set Value |
|------|-------|
| Output Format | 1 |
| Fields present | 16
| HW Mounting Position | 1 |
| Baud Rate | 2 |
| Set-Reset Rate | 100 |
| Output Rate | 1 |
| Averaging | 0 |
| AD Rate | 1 |
| Skip First Reaings | 0
| Euler Math | 4 |
| Deviation | 0.0 |
| Declination | 0.0 |

After the parameters are updated, the power to the OS4000-T shall be cycled.

### Comparison of on-board flash to expected values
From the OS4000-T retreived values, all of the following conditions must be met in order to receive a passing value.

| Name | Minimum Value | Maximum Value | Expected Value |
|------|-------|------|-------|
|Firmware Version | V2.6.4 | | |
|	Firmware Date	date | 01/01/2010 | | |
| Serial Number | 0 | 99999999| |
| Test Date | 01/01/2017 | | |
| Output Format | 1 | 16 |1,1|
| Fields present | 1 | 31 | 16 |
| HW Mounting Position | 1 | 6 | 4 |
| Baud Rate | 0 | 6 | 2 |
| Set-Reset Rate | 0 | 2400 | 100 |
| Output Rate | -50 | 40 | 1 |
| Averaging | 0 | 16 | 0 |
| AD Rate | 1 | 6 | 1 |
| Skip First Reaings | 0 | 20 | |
| Depth Offset | 0 | 1000 | |
| Max PSI | 0 | 3000 | |
| Euler Math | 1 | 4 | |
| Deviation | -1800 | 1800 | |
| Declination | -1800 | 1800 | |
| Temperature Offset | -999 | 999 | |
| Acceleration X Offset | -99999 | 99999 | |
| Acceleration Y Offset | -99999 | 99999 | |
| Acceleration Z Offset | -99999 | 99999 | |
| Acceleration X Scale | -99999 | 99999 | |
| Acceleration Y Scale | -99999 | 99999 | |
| Acceleration Z Scale | -99999 | 99999 | |
| Magnetometer X Offset | -9999 | 99999 | |
| Magnetometer Y Offset | -9999 | 99999 | |
| Magnetometer Z Offset | -9999 | 99999 | |
| Magnetometer X Offset Factor | -9999 | 99999 | |
| Magnetometer Y Offset Factor | -9999 | 99999 | |
| Magnetometer Z Offset Factor| -9999 | 99999 | |
| Temperature Calibration | -99999 | 99999 | |
| Magnetometer X Scale | -99999 | 99999 | |
| Magnetometer Y Scale | -99999 | 99999 | |
| Magnetometer Z Scale | -99999 | 99999 | |
| Magnetometer X Scale HT | -99999 | 99999 | |
| Magnetometer Y Scale HT | -99999 | 99999 | |
| Magnetometer Z Scale HT | -99999 | 99999 | |
| Magnetometer X Bridge Offset | -99999 | 99999 | |
| Magnetometer Y Bridge Offset | -99999 | 99999 | |
| Magnetometer Z Bridge Offset | -99999 | 99999 | |
| Total Gauss | 0 | 99999 | |
| Soft Iron Calibration | -99999 | 99999 | | 

### Calibration of OS4000-T
After completion of setting, reading and comparing the command variables (previous sections), the test should run a full Calibration for heading, pitch and roll.  

### Post Calibration Check
After the calibration is complete, the OS4000-T shall be tested on the four cardinal points to verify that the heading is within +/- 1 degree.  The pitch shall be tested at -45, 0 and +45 degrees in both pitch and roll to verify the angle is measured within 1 degree.

Failure of any of the previously mentioned conditions results in a test failure for the OS4000-T under test.

### Automation of Test for Multiple Units
Althought these tests could be run individually, the time it would take to test and calibrate 250 units would be prohibitive.  Therefore, the test will utilize a custome Printed Circuit Board (PCB) described below.  

To assist with running multiple OS4000-T simultaneously, an object based on an OS4000-T class should be developed from the start.  The class should contain:
1. Method to connect over serial port (Com port provided at \__init__)
1. Command of connected device (Setting variables, requesting data, etc.)
1. Parsing of any messages returned from the device.
1. Variable storage for comparison
1. Exceptions for invalid responses or errors.  The code shall not hard fail out of a script, thus killing all code running.  


### CSV generation
The test script shall create a CSV file for each test run that saves the following
data:

>OS_serial_number, OS_deviation, PMEL_owner, PMEL_test_date, PMEL_current_draw, PMEL_test_result

where:

  * OS_serial_number is the onboard serial number set by Ocean-Server
  * PMEL_owner is which group owns the sensor.  Valid values are:
    * "GTMBA"
    * "OCS"
    * "EDD"
    * "TEST"
  * PMEL_test_date is the date the device was tested
  * PMEL_current_draw is the device current measurement during operation.
  * PMEL_test_result is the final pass/fail of the test.  Valid values are:
    * True
    * False

The CSV file shall contain the header in the first line of every file.

An example file would look like:

> OS_serial_number, OS_deviation, PMEL_owner, PMEL_test_date, PMEL_test_result <br>
> 0017892, 0.0, EDD, 2017-09-07, True <br>
> 0017893, 0.0, OCS, 2017-09-07, False


## Test Hardware
The test hardware shall be a simple design.  

1. There shall be a PCB designed to allow for eight (8) OS4000-T modules to be oriented in the same direction.
1. The PCB shall be designed to fit onto the geodetic monument utilizing the PMEL test gimbal.
1. The PCB shall have a power input to allow for external batteries to power at the proper Number
of compass modules simultaneously for two (2) hours at minimum.
1. A USB hub should be used to allow for one (1) USB connection to control a minimum of eight (8) devices.
1. The USB hub shall be connected to the OS4000-T modules via a TTL UART connection.

## Guideline for Coding, etc.
1. Test code should be kept in a PMEL Github repository.
1. Test PCB schematics and layout should be maintained in the same repo.
1. Documentation for the test should be maintained in that repo.
1. Python should be used for this project
  1. PySerial should be used to interface to the compasses

1. Use Google Python Style Guide for commenting, etc. <br>
  http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html <br>
  https://google.github.io/styleguide/pyguide.html <br>
