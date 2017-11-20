import serial
import time

disallowed_commands = ['%']
nullary_commands = ['&','F']
unary_commands = ['R']

def _write_command(self,shortcomand:str) -> None:
    '''
    Initiates an escape sequence style command
    '''
    self.read_all()
    self.write(chr(27).encode())
    self.read_until(terminator='CMD:\r\n')
    self.write(shortcomand.encode())

def command(self,shortcommand,*args):
    '''
    Wrapper for all command types, handling marshaling and return formats
    '''
    
    if len(args)>0:
        fmtarg0 = "{}\r".format(args[0])
    if shortcommand in disallowed_commands:
        raise ValueError("Change Escape Character command (%) disallowed")
    elif shortcommand == '&':
        _write_command(self,shortcommand)
        time.sleep(1.0)
        result = self.read_until('OS5000-S')
        result += self.read_until()
        ser.write(32)
        ser.read_until()
        return result.decode('utf8')
    elif shortcommand in ['R','X','E','D','A']
        _write_command(self,shortcommand)
        result = str(self.read_until('Esc'))
        self.write(fmtarg0.encode())
    else:
        pass
    return

def paramdump_to_dict(paramdump):
    lines = [line for line in paramdump.replace("\r","").split('\n') if line not in '\n']
    paramdict = dict([line.split('=') for line in lines[1:-1]])
    paramdict['footer'] = lines[-1]
    return paramdict

# connect to device
ser = serial.Serial(
    port='/dev/cu.usbserial',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout = 2.0,
    write_timeout = 2.0)

# dump params
paramdump = command(ser,'&')
paramdict = paramdump_to_dict(paramdump)
print("\n")
print("Parameters:")
for key,value in paramdict.items():
    print("{0} = {1}".format(key,value))
time.sleep(5.0)

#set output rate
command(ser,'R',2)
print('\nOutput Rate set\n')
time.sleep(5.0)

# dump params
paramdump = command(ser,'&')
paramdict = paramdump_to_dict(paramdump)
print("\n")
print("Parameters:")
for key,value in paramdict.items():
    print("{0} = {1}".format(key,value))
time.sleep(5.0)

#close port
ser.close()
print('Port closed')
