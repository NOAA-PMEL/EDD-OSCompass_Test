import serial
import time

def compass_conn(port,baudrate=19200):
    '''
    Returns connection to an OS5000 on the given port
    '''
    conn = serial.Serial(port=port,
                         baudrate=baudrate,
                         parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE,
                         bytesize=serial.EIGHTBITS,
                         timeout = 2.0,
                         write_timeout = 2.0)
    return conn

#command long and short names by command type
interactive_commands = {'help':'H'}
report_commands = {'paramdump':'&',
                   'FW_Version':'V'}
calibration_commands = {'Calibrate_XY':'C',
                        'Calibrate_Z':'Z',
                        'Temperature_cal':'+'}
set_commands = {'Output_Rate':'R',
                'Baud_Rate':'B',
                'Display_Fields':'X',
                'Declination':'Q',#coincides with deviation setting?
                'Averaging':'A',
                'HW_Mounting_Pos':'E',
                'AD_Update_Rate':'D',
                'Output_Format':'*'}
#set commands unassigned for:
# Deviation (though possibly tied to declination setting routine)
# Skip First Readings
# Euler Math
# Set-Reset Rate

disallowed_commands = {'%':"Change Escape Character command (%) disallowed"}

shortcommands = {**interactive_commands,
                 **report_commands,
                 **calibration_commands,
                 **set_commands}


def _write_command(self,shortcomand):
    '''
    Initiates an escape sequence style command
    '''
    self.read_all()
    self.write(chr(27).encode())
    self.read_until(terminator='CMD:\r\n')
    self.write(shortcomand.encode())

def command(self,commandstr,*args):
    '''
    Wrapper for all command types, handling marshaling and return formats
    '''
    # translate long name commands into short equivalent
    if len(commandstr) < 1:
        raise(ValueError('Empty string no valid command'))
    elif len(commandstr) > 1:
        # send short command with possible args
        return command(self,shortcommands[commandstr],*args)
    else:
        if commandstr in disallowed_commands.keys():
            raise ValueError(disallowed_commands[commandstr])
        elif commandstr in report_commands.values():
            _write_command(self,commandstr)
            time.sleep(1.0)
            result = self.read_until('OS5000-S')
            result += self.read_until()
            self.write(32)
            self.read_until()
            return result.decode('utf8')
        elif commandstr in set_commands.values():
            _write_command(self,commandstr)
            result = str(self.read_until('Esc'))
            self.write("{}\r".format(args[0]).encode())
        else:
            raise ValueError("Invalid OS5000 command")
    return
