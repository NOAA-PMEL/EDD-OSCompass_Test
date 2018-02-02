import serial
import time


#command long and short names by command type
interactive_commands = {'help':'H'}
report_commands = {'paramdump':'&',
                   'FW_Version':'V'}
set_commands = {'Output_Rate':'R',
                'Baud_Rate':'B',
                'Display_Fields':'X',
                'Declination':'Q',#coincides with deviation setting?
                'Averaging':'A',
                'HW_Mounting_Pos':'E',
                'AD_Update_Rate':'D',
                'Output_Format':'*'}
cal_commands = {'XY_Cal':'C',
                'Z_Cal':'Z',
                'Soft_Iron':'$'}
ser_commands = {'Flush':'Flush'}

         

#set commands unassigned for:
# Deviation (though possibly tied to declination setting routine)
# Skip First Readings
# Euler Math
# Set-Reset Rate

#disallowed_commands = ['%']
disallowed_commands = {'%':"Change Escape Character command (%) disallowed"}
shortcommands = {**interactive_commands,
                 **report_commands,
                 **cal_commands,
                 **set_commands}


def _write_command(self, shortcommand):
    '''
    Initiates an escape sequence style command
    '''
    #self.read_all()
    self.flushInput()
    self.write(chr(27).encode())
    self.read_until(terminator='CMD:')
    self.write(shortcommand.encode())

    
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
        elif commandstr in '&':#report_commands.values():
            _write_command(self,commandstr)
            time.sleep(1.0)
            result = self.read_until(terminator=b'SoftIron')   #Read some arbitrary distance into Paramdump. 
            result += self.read_until(terminator=b'OS4000-T')  #Grab 2nd 'OS4000-T' string
            result += self.read_until()             #Finish reading until last line
            self.write(chr(32).encode())            #Send <Space> to begin streaming of compass data again
            return result.decode('utf-8')            #return Paramdump
        elif commandstr in 'V':
            _write_command(self, commandstr)
            time.sleep(0.25)
            result = self.readline()
            result += self.readline()
            self.write(chr(32).encode())
            return result.decode()
        elif commandstr in set_commands.values():
            _write_command(self,commandstr)
            print(self.read_until(terminator=b'Esc').decode())
            self.write("{}\r".format(args[0]).encode())
            self.read_until(terminator=b'Flash Write')
        else:
            raise ValueError("Invalid OS4000-T command")
    return

def cal(self,commandstr,*args):
    
    """Start"""
    if commandstr in cal_commands:
        self.read_all()
        _write_command(self, cal_commands[commandstr])
        if cal_commands[commandstr] in '$':
            self.write(cal_commands[commandstr].encode())
            time.sleep(0.5)
            self.read_until(terminator=b'Esc').decode()
            self.write("{}\r".format(args[0]).encode())
            self.read_until(terminator=b'Bar>')
        else:
            self.read_until(terminator=b'done').decode()
    elif commandstr in "Step":
        self.flushInput() #Gets rid of 'xYxXy.xy..X'
        self.write(chr(32).encode())
        #print(self.read_until(terminator=b'Flash Write').decode())
    elif commandstr in "Soft_Step":
        self.write(chr(32).encode())
        #assert read statement below receives 'Bar>'
        #print(self.read_until(terminator=b'Bar>').decode())
    elif commandstr in "SoftIron_Step":
        self.write(chr(32).encode())
        input = self.read_until(terminator=b'continue **').decode()
        print("Soft Iron Cal: %s" % (input[input.find("Deviation"):input.rfind("Hit")-4]))
        self.write(chr(32).encode())
        time.sleep(0.25)
        
        print(self.read_until(terminator=b'Flash Write').decode())
        #assert input == 'Flash Write'
    elif commandstr in "Flush":
        self.flushInput()
        
        
        
