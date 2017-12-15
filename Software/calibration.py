import csv
import time

import device
import params

def calibrate(port):
    '''
    Run automated parameter setting and calibration for the device at the specified port
    '''
    # configure the serial connections (the parameters differs on the device you are connecting to)
    with device.compass_conn(port) as ser:
        print("Port open = {}".format(ser.isOpen()))

        #confirm data can be read
        data = ser.read_until().decode()
        print("Data string = {}".format(data))

        # dump params into log
        paramdumpfname = '../data/paramdump.txt'
        paramdump = device.command(ser,'paramdump')
        with open(paramdumpfname, 'w') as paramdumpfile:
            paramdumpfile.write(paramdump)

        #load/parse params and print out
        with open(paramdumpfname, 'r') as paramdumpfile:
            paramdict = params.paramdump_to_dict(paramdumpfile.read())
        print("Parameters:")
        for key,value in paramdict.items():
            print("{0} = {1}".format(key,value))
        time.sleep(5.0)

        #load conditions are determine params outside of valid range
        conditions = params.param_conditions('../data/param_conditions.csv')
        bad_params = params.invalid_params(paramdict,conditions)

        #update settable params
        settable_params = [param for param in bad_params if param in device.set_commands.keys()]
        if settable_params:
            print("\nSetting parameters")
            for param in settable_params:
                current = paramdict[param]
                target = params.valid_param(conditions[param])
                device.command(ser,param,target)
                print("{param} : {current} --> {target} Done".format(param=param,
                                                                     current = current,
                                                                     target = target))
        else:
            print("No setable invalid parameters")

        #print out unsettable params
        unsettable_params = [param for param in bad_params if param not in device.set_commands.keys()]
        if unsettable_params:
            print('\nUnsetable invalid parameters:')
            for param in unsettable_params:
                print(param)
        else:
            print('\nNo unsetable invalid parameters:')
