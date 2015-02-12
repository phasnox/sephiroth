from datetime import datetime
from datetime import timedelta
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
SAMPLING_HZ     = 50

def str_to_time(time_str):
    return datetime.strptime(time_str, DATETIME_FORMAT)

def time_to_str(time_value):
    return datetime.strftime(time_value, DATETIME_FORMAT)

# TODO Horrible naming
def get_values(data):
    data = data.split(';')
    return {
        'time': data[0], 
        'value': float( data[1] )
    }

def find_index(data, time_value):
    # Binary search
    i     = len(data) / 2
    index = i
    while i>0:
        time_i = str_to_time(data[i]['time'])
        if time_i == time_value: break
        if time_i > time_value:
            data = data[0:i]
            i = i/2
            index = index - i
        else:
            data = data[i:len(data)]
            i = i/2
            index = index + i
    print 'Index: %d' % index
    return index

def find_index_linear(data, time_value):
    index = 0
    for point in data:
        time_i = str_to_time(point['time'])
        if time_i >= time_value: break
        index = index + 1
    print 'Index: %d = %s' % (index, time_to_str(time_value))
    return index

def get_time_str(i, ref_time):
    return time_to_str(ref_time + timedelta(0,0,0, i*5))
