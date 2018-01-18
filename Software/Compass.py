#OS4000T Class for Compass Calibration Software
import math
import time
import os, stat, sys, glob, serial
import calibration
import device
import csv
import pandas

MAX_COMPASS_DEVIATION=1.0
MAX_PITCH_DEVIATION=2.0
MAX_ROLL_DEVIATION=2.0

class OS4000T():

    def __init__(self, port, baud):

        self.port = port
        self.ser=self.Open_ComPort(baud)
        self.installed=False
        #Grab example output from compass. Ex: $C106.3P-15.6R46.0T20.4*0A
        if(self.grab_compass_example()==-1):
            if(baud==9600):
                baud=19200
            else:
                baud=9600
            self.grab_compass_example()
        
        self.serialNumber = 0
        self.current = 0
        self.testResult = False
        self.deviation = 0.0
        
        
    def Open_ComPort(self, baud):
        
        conn = serial.Serial(port=self.port,
            baudrate=baud,
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
                ex = input[input.rfind("$"):input.rfind("*")+3]
                print("%s: %s" % (self.port, ex))
                self.installed=True
                return ex
            else:
                return -1
        else:
            return -1

                
   
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
    

def write_csv(compass, date, owner):
    
    if(os.path.isfile('OS4000T.csv')==False):
        f = open('OS4000T.csv', 'a')
        f.write("Serial Number,Deviation,PMEL Owner,Test Date,Compass Current,Test Result\r\n")
    else:
        f = open('OS4000T.csv', 'a')
    f.write("%s,%s,%s,%s,%s,%s\r\n" %(compass.serialNumber, compass.deviation, owner, date, compass.current, compass.testResult))
    f.close()
    
def update_csv(compass, timenow):
    file = open('OS4000T.csv', newline='')
    CompassReader = pandas.read_csv(file, delimiter=',')
    df = pandas.DataFrame(data=CompassReader)
        
        
    df = df.set_index('Serial Number')
    df = df.sort_index()
    df = df[~df.index.duplicated(keep='last')]
    
        
    for i in range(8):
        if(compass[i].installed):
            num = int(compass[i].serialNumber)
            df.ix[num, 0] = compass[i].deviation
            df.ix[num, 2] = timenow
            df.ix[num, 4] = compass[i].testResult
        
    print(df)
    
    #Write sorted file to list.
    dataList.to_csv('OS4000T_Master.csv')
    
    
def compass_setup(Ports):
    compass=[]

    
    owner= input('PMEL Owner: ')

    for i in range(8):
        compass.append(OS4000T(Ports[len(Ports)-8+i], 9600))
        
    for i in range(8):
        if(compass[i].installed):
            calibration.parameter_dump(compass[i], "Params_PreCal")
            calibration.parameter_check(compass[i], "Params_PreCal")
    
    print("Compass current testing. 1 milli-Volt equals 10 milli-Amp")     
    for i in range(8):
        if(compass[i].installed):
            calibration.current_monitor(compass[i])		
    
    datetime = time.strftime("%m%d%Y_%H:%M:%S", time.gmtime())        
    for i in range(8):
        if(compass[i].installed):
            write_csv(compass[i], datetime, owner)
            
    input("Unplug USB device, reconnect, then wait 10 seconds for settings to take effect. Then press enter.")            


def compass_calibrate(Ports):
    compass=[]
    
    for i in range(8):
        compass.append(OS4000T(Ports[len(Ports)-8+i], 9600))
            
    calibration.calibrate_xy(compass)

    calibration.calibrate_z(compass)

    calibration.calibrate_softiron(compass)
    

    for i in range(8):
        if(compass[i].installed):
            calibration.parameter_dump(compass[i], "Params_PostCal")
    
    datetime = time.strftime("%m%d%Y_%H:%M:%S", time.gmtime())
    
    test_verification(compass)
    
    #Push new Compass Values
    update_csv(compass, datetime)

def test_verification(compass):
    #Assuming they pass unless proven not below
    for i in range(8):
        compass[i].testResult=True
    
    print("Testing accuracy of calibration. ")
    for i in range(5):
        direction = int(input("Turn compass calibration jig to desired direction and enter degree (0-359):"))
        if(0<=direction<=359):
            for i in range(8):
                if(compass[i].installed & compass[i].testResult):
                    ex = compass[i].grab_compass_example()
                    c = ex[ex.find("$C")+2:ex.rfind("P")]
                    result = math.fabs(float(c)-direction)
                    print("Compass %s deviation: %s" %(compass[i].serialNumber, result))
                    if(result>=MAX_COMPASS_DEVIATION):
                        compass[i].testResult=False
                        print("Compass Failed!")

    print("Testing Pitch Accuracy")
    for i in range(4):
        pitch = int(input("Pitch compass calibration jig to desired angle (-75 to 75):"))
        if(-75<=pitch<=75):
            for i in range(8):
                if(compass[i].installed & compass[i].testResult):
                    ex = compass[i].grab_compass_example()
                    p = ex[ex.find("P")+1:ex.rfind("R")]
                    result = math.fabs(float(p)-pitch)
                    print("Compass %s pitch deviation: %s" %(compass[i].serialNumber, result))
                    if(result>=MAX_PITCH_DEVIATION):
                        compass[i].testResult=False
                        print("Compass Failed!")
    
    print("Testing Roll Accuracy")
    for i in range(4):
        roll = int(input("Roll compass calibration jig to desired angle (-75 to 75):"))
        if(-75<=roll<=75):
            for i in range(8):
                if(compass[i].installed & compass[i].testResult):
                    ex = compass[i].grab_compass_example()
                    r = ex[ex.find("R")+1:ex.rfind("T")]
                    result = math.fabs(float(r)-roll)
                    print("Compass %s roll deviation: %s" % (compass[i].serialNumber, result))
                    if(result>=MAX_ROLL_DEVIATION):
                        compass[i].testResult=False
                        print("Compass Failed!")
    
    

Ports=Setup_ComPorts()	

while(1):

    char = input("Compass Setup (\'s\') or Compass Calibrate (\'c'\')?")
    print("Input Char: %s" % char)
    
    if(char=='s'):
        compass_setup(Ports)
    elif(char=='c'):
        compass_calibrate(Ports)
    elif(char==''):
        break
