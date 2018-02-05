#OS4000T Class for Compass Calibration Software
import math
import time
import os, stat, sys, glob, serial
import calibration
import device
import csv
import pandas

MAX_COMPASS_DEVIATION=1.01
MAX_PITCH_DEVIATION=5.01
MAX_ROLL_DEVIATION=5.01

class OS4000T():

    def __init__(self, port, baud):

        self.port = port
        self.ser=self.Open_ComPort(baud)
        self.installed=False
        #Grab example output from compass. Ex: $C106.3P-15.6R46.0T20.4*0A
        a = self.grab_compass_example()
        if(a == -1):
            self.ser.close()
            if(baud==9600):
                baud=19200
            else:
                baud=9600
            self.ser = self.Open_ComPort(baud)
            self.grab_compass_example()
        elif(a == 0): 
            return
        self.grab_serial_number()
        self.current = 0
        self.testResult = False
        self.deviation = 0.0
        self.headingDev=0.0
        self.pitchDev=0.0
        self.rollDev=0.0
        if(self.serialNumber):
            print("%s: SN#%s" % (self.ser.port, self.serialNumber))
        
        
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
        self.ser.readline()
        input=self.ser.readline().decode()
        
        #input = self.ser.read_until().decode('utf-8', 'ignore')
        if(input.find("$")!=-1):
            if(input.rfind("*")!=-1):
                ex = input[input.rfind("$"):input.rfind("*")+3]
                #print("%s: %s" % (self.port, ex))
                self.installed=True
                return ex
            else:
                return -1
        elif(input==''):
            print("Nothing in %s" % self.port)
            return 0
        else:
            return -1
            
    def grab_compass_line(self):
        self.ser.readline()
        
        
        input = self.ser.readline().decode('utf-8', 'ignore')
        
        input = input[input.rfind("$"):input.rfind("*")+3]
        print("Compass %s: %s" % (self.serialNumber, input))
        return input

    def grab_serial_number(self):
        result = device.command(self.ser, "FW_Version")
        #print(result)
        self.serialNumber= result[result.find("SN#")+3:result.rfind(",")]
        #print("Compass %s on %s" % (self.serialNumber, self.port))
   
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
    

def write_csv(compass, owner):
    date = time.strftime("%m%d%Y_%H:%M:%S", time.gmtime())      
    if(os.path.isfile('OS4000T.csv')==False):
        f = open('OS4000T.csv', 'a')
        f.write("Serial Number,Deviation,PMEL Owner,Test Date,Compass Current,Test Result,Average Heading Deviation,Average Pitch Deviation,Average Roll Deviation\r\n")
    else:
        f = open('OS4000T.csv', 'a')
    f.write("%s,%s,%s,%s,%s,%s,%s,%s,%s\r\n" %(compass.serialNumber, compass.deviation, owner, date, compass.current, compass.testResult, compass.headingDev, compass.pitchDev, compass.rollDev))
    f.close()
    
def update_csv(compass):
    file = open('OS4000T.csv', newline='')
    CompassReader = pandas.read_csv(file, delimiter=',')
    df = pandas.DataFrame(data=CompassReader)
        
        
    df = df.set_index('Serial Number')
    df = df.sort_index()
    df = df[~df.index.duplicated(keep='last')]
    timenow = time.strftime("%m%d%Y_%H:%M:%S", time.gmtime())
        
    for i in range(8):
        if(compass[i].installed):
            num = int(compass[i].serialNumber)
            df.ix[num, 0] = compass[i].deviation
            df.ix[num, 2] = timenow
            df.ix[num, 4] = compass[i].testResult
            df.ix[num, 5] = compass[i].headingDev
            df.ix[num, 6] = compass[i].pitchDev
            df.ix[num, 7] = compass[i].rollDev
        
    print(df)
    
    #Write sorted file to list.
    df.to_csv('OS4000T_Master.csv')
    
    
def compass_setup(Ports, compass):
    

    
    owner= input('PMEL Owner: ')
    if(compass==[]):
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
    
      
    for i in range(8):
        if(compass[i].installed):
            write_csv(compass[i], owner)
            
    input("Unplug USB device, reconnect, then wait 10 seconds for settings to take effect. Then press enter.")            


def compass_calibrate(Ports, compass):
    
    if(compass==[]):
        for i in range(8):
            compass.append(OS4000T(Ports[len(Ports)-8+i], 9600))
            
    calibration.calibrate_xy(compass)

    calibration.calibrate_z(compass)

    calibration.calibrate_softiron(compass)
    

    for i in range(8):
        if(compass[i].installed):
            calibration.parameter_dump(compass[i], "Params_PostCal")

    
    
    
def test_verification(Ports, compass):
    headingCount = 0
    if(compass==[]):
        for i in range(8):
            compass.append(OS4000T(Ports[len(Ports)-8+i], 9600))

    #Assuming they pass unless proven not below
    for i in range(8):
        if(compass[i].installed):
            compass[i].testResult=True
    
    print("Testing accuracy of calibration. ")
    for i in range(5):
        text = input("Turn compass calibration jig to desired direction and enter degree (0-359):")
        if(text==''):
            text='-1'
            print("Please pick a number between 0 and 359")
        direction = int(text)
        if(0<=direction<=359):
            calibration.all_compasses(compass, "Flush")
            headingCount +=1
            for i in range(8):
                if(compass[i].installed):
                    ex = compass[i].grab_compass_line()
                    c = ex[ex.find("C")+1:ex.rfind("P")]
                    result = math.fabs(float(c)-direction)
                    if(result > 180):
                        result = 360.0 - result
                    compass[i].headingDev += result
                    print("Compass %s deviation: %s" %(compass[i].serialNumber, result))
                    #If direction = 0, test for results +/- 1.1 from North. I.E. 389.9 to 1.1 degrees
                    if(direction==0):
                        #If deviation in range of 1.1 to 358.9 test failed
                        if(358.9>=result>=MAX_COMPASS_DEVIATION):
                            compass[i].testResult=False
                            print("Compass Failed!")
                    #For all other directions != 0                        
                    elif(result>=MAX_COMPASS_DEVIATION):
                        compass[i].testResult=False
                        print("Compass Failed!")

    for i in range(8):
        if(compass[i].installed):
            compass[i].headingDev = compass[i].headingDev/headingCount                        
                        
    pitchCount =0
    print("Testing Pitch Accuracy")
    for i in range(4):
        text = input("Pitch compass calibration jig to desired angle (-75 to 75):")
        if(text == ''): 
            text = '76'
            print("Please pick a number between -75 and 75")
        pitch = int(text)
        if(-75<=pitch<=75):
            calibration.all_compasses(compass, "Flush")
            pitchCount += 1
            for i in range(8):
                if(compass[i].installed):
                    ex = compass[i].grab_compass_line()
                    p = ex[ex.find("P")+1:ex.rfind("R")]
                    result = math.fabs(float(p)-pitch)
                    compass[i].pitchDev += result
                    print("Compass %s pitch deviation: %s" %(compass[i].serialNumber, result))
                    
    
    for i in range(8):
        if(compass[i].installed):
            compass[i].pitchDev = compass[i].pitchDev/pitchCount   
            if(compass[i].pitchDev>=MAX_PITCH_DEVIATION):
                compass[i].testResult=False
                print("Compass %s Failed!" % compass[i].serialNumber)
    
    rollCount = 0
    print("Testing Roll Accuracy")
    for i in range(4):
        text =input("Roll compass calibration jig to desired angle (-75 to 75):")
        if(text == ''): 
            text = '-76'
            print("Please pick a number between -75 and 75")
        roll = int(text)
        if(-75<=roll<=75):
            calibration.all_compasses(compass, "Flush")
            rollCount += 1
            for i in range(8):
                if(compass[i].installed):
                    ex = compass[i].grab_compass_line()
                    r = ex[ex.find("R")+1:ex.rfind("T")]
                    result = math.fabs(float(r)-roll)
                    compass[i].rollDev += result
                    print("Compass %s roll deviation: %s" % (compass[i].serialNumber, result))
                    
    
    
    for i in range(8):
        if(compass[i].installed):
            compass[i].rollDev = compass[i].rollDev/rollCount
            if(compass[i].rollDev>=MAX_ROLL_DEVIATION):
                compass[i].testResult=False
                print("Compass %s Failed!" % compass[i].serialNumber)
    
    #Push new Compass Values
    update_csv(compass)


Ports=Setup_ComPorts()  
compass = []
while(1):
    
    char = input("Compass Setup (\'s\'), Calibrate (\'c\') or Verification (\'v\')?")
    #print("Input Char: %s" % char)
    
    if(char=='s'):
        compass_setup(Ports, compass)
    elif(char=='c'):
        compass_calibrate(Ports, compass)
    elif(char=='v'):
        test_verification(Ports, compass)
    elif(char==''):
        break
