#OS4000T Class for Compass Calibration Software

import time
import serial
import os, stat, sys, glob, serial
import calibration
import device


class OS4000T():

    def __init__(self, port):
        
        self.port = port
        self.ser=self.Open_ComPort()
        self.installed=False
        #Grab example output from compass. Ex: $C106.3P-15.6R46.0T20.4*0A
        self.grab_compass_example()
        self.serialNumber = 0
        self.current = 0
		
	
        
    def Open_ComPort(self):
        
        conn = serial.Serial(port=self.port,
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout = 2.0,
            write_timeout = 2.0)
        return conn
    
    def grab_compass_example(self):
        self.ser.flushInput()
        #input = self.ser.readline().decode()
        input = self.ser.readline().decode('utf-8', 'ignore')
        if(input.find("$")!=-1):
            if(input.rfind("*")!=-1):
                print("%s: %s" % (self.port, input[input.rfind("$"):input.rfind("*")+3]))
                self.installed=True
                
   
def Setup_ComPorts():
    portnames =[]
    
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i+1) for i in range(256)]
        #print("Windows")
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported Platform')
        
    portnames[:] = []
    for port in ports:
        try:
            s = serial.Serial(port)
            
            s.close()
            portnames.append(port)
        except (OSError,serial.SerialException):
            pass
    #        
    
    print(portnames)
    return(portnames)
    
""" Moved to Calibration.py    
def all_compasses(compass, command, *args):
    for i in range(8):
        input = ""
        if(compass[i].installed):
            device.cal(compass[i].ser,command, *args)
""" 
        
    
Ports=Setup_ComPorts()
compass=[]

date= input('Test Date mmddyyyy: ')
owner= input('PMEL Owner: ')

for i in range(8):
    compass.append(OS4000T(Ports[len(Ports)-8+i]))
    
for i in range(8):
    if(compass[i].installed):
        calibration.parameter_dump(compass[i], "Params_PreCal")
        calibration.parameter_check(compass[i], "Params_PreCal")

for i in range(8):
	if(compass[i].installed):
		calibration.current_monitor(compass[i])		
		
for i in range(8):
	if(compass[i].installed):
		print("Compass %s: SN# %s" % (i, compass[i].serialNumber))

calibration.calibrate_xy(compass)

calibration.calibrate_z(compass)

calibration.calibrate_softiron(compass)

for i in range(8):
    if(compass[i].installed):
        calibration.parameter_dump(compass[i], "Params_PostCal")
		

	

