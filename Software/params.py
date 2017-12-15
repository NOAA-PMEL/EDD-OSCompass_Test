import csv
from distutils.version import LooseVersion
from datetime import datetime

def paramdump_to_dict(paramdump):
    '''
    Returns comparable value dictionary from parameter dump string
    '''
    lines = [line for line in paramdump.replace("\r","").split('\n') if line not in '\n']#this if statement is superfulous?
    paramdict_raw = dict([line.split('=') for line in lines[1:-1]])
    paramdict_raw['footer'] = lines[-1]#need to make a little more robust, or document guarantee in paramdump
    paramdict = {param:parse_param_value(param,value) for param,value in paramdict_raw.items()}
    return paramdict

def param_conditions(fname):
    '''
    Return a dict of dict containing maximum, minimum and expected paramter values for each parameter.
    '''
    with open(fname) as csv_file:
        param_conditions = csv.reader(csv_file, delimiter=',')
        next(param_conditions)
        conditions = {param : {'min' : parse_param_value(param,minval),
                               'max' : parse_param_value(param,maxval),
                               'expected' : parse_param_value(param,expectedval)}
                      for param,minval,maxval,expectedval in param_conditions}
        #del conditions['FW_Version']
    return conditions

def is_valid_param(param,condition):
    '''
    Returns True for params equal to expected value or, if no vallue expected, within interval of min/max.
    Returns False for params that don't meet these expectation or are nulllike.
    '''
    if param is None:
        return False
    elif condition['expected'] is None:
        return condition['min'] <= param <= condition['max']
    else:
        return param == condition['expected']

def valid_param(condition):
    '''
    Returns a valid target parameter based on the condition
    (currently middle of valid interval value if expected not specified).
    '''
    if condition['expected'] is None:
        return (condition['min']+condition['max'])/2
    else:
        return condition['expected']


def invalid_params(paramdict,conditions):
    '''
    Return a list of invalid params in the paramdict based on the specified conditions
    '''
    return [param for param,condition in conditions.items() if not is_valid_param(paramdict[param],condition)]

def parse_param_value(param,value):
    '''
    Parses the raw param string value based on param name.

    NOTES:
    Empty strings represented as None
    All num-like values converted to floating points.
    Date parsing valid through 2099 (see parse_date_str for details)
    Version numbers based on LooseVersion
    '''
    if value is '':
        return None
    elif param == 'FW_Date':
        return parse_date_str(value,sep='-')
    elif param == 'Test_date':
        return parse_date_str(value,sep=' ')
    elif param == 'FW_Version':
        return LooseVersion(value.replace('V','').replace('-','.'))
    elif param == 'Serial_number':
        return float(value.replace('[D',''))
    elif param in ['Depth_Units','footer']:
        return value
    else:
        fval = float(value)
        if fval.is_integer():
            return int(fval)
        else:
            return fval

def parse_date_str(datestr,sep = ' '):
    '''
    Return date object from date string after normalizing in the format known to be returned by compass.
    Assumes non zero padded day of month, abbreviated name of month and zero padded years since 2000.
    '''
    normdatestr = "{0:0>2} {1} 20{2}".format(*datestr.split(sep))
    return datetime.strptime(normdatestr, '%d %b %Y')
