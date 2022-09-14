def time_to_microsecs(string):
    """Formats a string with this time format - 00:00:00:000 - in microseconds."""

    hours = int(string[0:2]) * 3600000000
    minutes = int(string[3:5]) * 60000000 
    seconds = int(string[6:8]) * 1000000
    microseconds = int(string [9:12]) + hours + minutes + seconds
    return microseconds

def datatime_to_microsecs(string):
    """Formats a string with this time format - 0000/00/00 00:00:00.000 - in microseconds."""

    hours = int(string[12:14]) * 3600000000
    minutes = int(string[15:17]) * 60000000 
    seconds = int(string[18:20]) * 1000000
    microseconds = int(string [21:24]) + hours + minutes + seconds
    return microseconds

def array_to_microseconds(array,function):
    """Tranforms a given array of strings with a certain time format into microseconds by 
    making each element of the array go throught a given function."""
    
    array1 = []
    for line in array:
        time = function(line)
        array1.append(time)
    return array1