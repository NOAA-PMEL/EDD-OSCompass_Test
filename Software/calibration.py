import errno
import csv
import time
import os

import device
import params


def parameter_dump(compass, filename):
    '''
    Run automated parameter setting and calibration for the device at the specified port
    '''
    
    # dump params into log
    paramdump = device.command(compass.ser,'paramdump')
    #compass.serialNumber = (paramdump[paramdump.find("Serial_number=")+14:paramdump.find("Test_date")]).strip("\r\n")
    
    
    #Create Compass Serial Number directory if non-existent. 
    try:
        os.mkdir('%s/%s/' % (os.getcwd(), compass.serialNumber))
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise  
        pass
    
    #Save parameters into serial number directory
    paramfname = '%s/%s/%s.txt' % (os.getcwd(), compass.serialNumber, filename)
    with open(paramfname, 'w') as paramfile:
        paramfile.write(paramdump)
    paramfile.close()
    
    
def parameter_check(compass, filename):    

    paramfname = '%s/%s/%s.txt' % (os.getcwd(), compass.serialNumber, filename)
    #load/parse params and print out
    with open(paramfname, 'r') as paramfile:
        paramdict = params.paramdump_to_dict(paramfile.read())
    print("Saving parameters to %s.txt in directory: /%s/" % (filename, compass.serialNumber) )
    #for key,value in paramdict.items():
        #print("{0} = {1}".format(key,value))
    
    #load conditions are determine params outside of valid range
    conditions = params.param_conditions('./data/param_conditions.csv')
    bad_params = params.invalid_params(paramdict,conditions)
    if(bad_params):
        print("Bad Params: %s" % bad_params)
    
    #update settable params
    settable_params = [param for param in bad_params if param in device.set_commands.keys()]
    if settable_params:
        print("Setting parameters:")
        for param in settable_params:
            current = paramdict[param]
            target = int(params.valid_param(conditions[param]))
            #print("Target: %d" % target)
            device.command(compass.ser, param, target)
            print("{param} : {current} --> {target} Done".format(param=param,
                                                                 current = current,
                                                                 target = target))
    else:
        print("No settable invalid parameters")

    #print out unsettable params
    unsettable_params = [param for param in bad_params if param not in device.set_commands.keys()]
    if unsettable_params:
        print('Unsetable invalid parameters:')
        for param in unsettable_params:
            print(param)
    else:
        print('No unsetable invalid parameters')
        
    paramfile.close()
    
def all_compasses(compass, command, *args):
    for i in range(8):
        if(compass[i].installed):
            device.cal(compass[i].ser,command, *args)

            
def calibrate_xy(compass):                    
    input("Level compass module and press <Enter> to begin XY calibration")

    all_compasses(compass, "XY_Cal")

    input("Rotate Compass 360 degrees over 20 seconds then press <Enter>")

    all_compasses(compass, "Step")

def calibrate_z(compass):
    input("Roll Compass to 90 degrees to perform Z axis calibration. Press <Enter> when ready")

    all_compasses(compass, "Z_Cal")

    input("Rotate Compass 360 degrees over 20 seconds then press <Enter>")

    all_compasses(compass, "Step")

def calibrate_softiron(compass):   
    print("Return Compass roll back to level.")
    direction = ["North, 0", "East, 90", "South, 180", "West, 270"]   
    all_compasses(compass, "Soft_Iron", "2")
    for i in range(3):
        input("Align exactly %s degrees, then hit <Enter>" % direction[i])
        all_compasses(compass, "Soft_Step")
    
    input("Align exactly %s degrees, then hit <Enter>" % direction[3])
    all_compasses(compass, "SoftIron_Step")
    

        

def current_monitor(compass):
	compass.current = input("Compass #%s?" % compass.serialNumber ) 
