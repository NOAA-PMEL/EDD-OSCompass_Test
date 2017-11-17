# Basic Test Requirements for OS4000-T Compass Modules
Author: Matt Casari <br>
Date: August 22, 2017

## Overview
Ocean-Server has recently sent out a "Last-Buy" for the entire product line of
digital compass modules.  PMEL had just completed testing and integration of the
OS4000-T module into the FLEX and the new ICM modules.  PMEL has decided to
purchase a large quantity of these modules (250 units) to cover the projected need
for the next three to five years of production.  

Ocean-Server will honor the 1-year warranty from time of purchase for these devices.
Since there is no extended warranty option, it is in PMEL's best interest to
validate these compasses upon delivery in order to have Ocean-Server fix or
replace any faulty unit.

## Proposed Test Method
Since there will be 250 units to test, it would be benefitial to test as many
of the sensors simultaneously as possible.  This can be done by having a precision
test backplace built (either milled+wired or PCB) so that multiple units can
be tested at the same time.  This could utilize a The test jig should fit into the monument located
behind building 3 so that heading testing can easily be accomplished.

Testing should be designed to include the following:

1. Test Powerup/Connection to devices
1. Set Compass settings for FLEX (detailed below)
1. Retreive system information (detailed below)
1. Test compass module on the cardinal points (using PMEL monument)


### Compass settings
The FLEX system runs the compass module at 9600 baud.  On initial connection to
the OS4000-T, the test should reconfigure the compass to run at 9600 baud.  This
will provide a consistent baud rate over all systems and reduce configuration
time by engineers and technicians.

There are other settings that must be changed.  They are as follows:

1. Baud Rate: 9600
1. Output Rate: 5 samples/sec
1. Skip n first readings: 0
1. Set-Reset Rate: 100 sentences
1. Euler Math: 4
1. Average Samples: 4
1. AD Decimation Filter: 3

### Variables to compare and track

Once the settings have been updated, the test program should grab them and from
the compass memory and compare against expected values (as denoted in parentheses)

1. Serial Number (***variable***)
1. Firmware Version (***variable***)
1. Firmware Date (***varibable***)
1. Output Format  (***cmdOutFormatC***)
1. Fields Present (***15***)
1. Test Date (***variable***)
1. Baud Rate (***3***)
1. HW Mounting Position (***1***)
1. Set-Reset Rate (***100***)
1. Output Rate (***5***)
1. Averaging  (***4***)
1. AD Update Rate  (***3***)
1. Skip First Readings (***0***)
1. Euler Math (***4***)
1. Temperature Offset (***variable***)

In addition to the system data, the four cardinal points should be measured and
compared to actual:
1. North (***0&deg;***)
1. East (***90&deg;***)
1. South (***180&deg;***)
1. West (***270&deg;***)


### Test Failures
A test will be considered a failure IF:
1. The system does not power on or return any values
1. The returned system value for any variable updated at the beginning of the test is not equivalent
1. Any of the cardinal point measurements exceeds +/- 5&deg;

### Retest of Failed units
After all 250 compasses are tested, the failures shall be retested.  

1. If the failures is due to power on errors, the compass shall be tested individually.
1. If the compass failed the cardinal point test, it shall be fully calibrated by hand.
1. If the compass failed to have settings updated, it shall be retested manually.

## Data Tracking
The data for each compass needs to be tracked.  A database would be the best
possible option, but to minimize time requirements for establishing these tests,
a simple Excel or .csv file will suffice.  

## Guideline for Coding, etc.
1. Test code should be kept in a PMEL Github repository.
1. Documentation for the test should be maintained in that repo.
1. Python should be used for this project
  1. PySerial should be used to interface to the compasses

1. Use Google Python Style Guide for commenting, etc. <br>
  http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html <br>
  https://google.github.io/styleguide/pyguide.html <br>
