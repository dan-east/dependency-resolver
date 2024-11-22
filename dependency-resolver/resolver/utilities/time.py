import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__) # module name

# Get the current date and time as a string.
def getCurrentDateTimeString(format:str = "%d/%m/%Y %H:%M:%S") :
    return datetime.now().strftime(format)


# Returns the time delta from the given timestamp to now.
#  that is how old is the given timestamp. 
def howOld(timestamp:int) -> timedelta:
    return datetime.today() - datetime.fromtimestamp(timestamp)


# Returns how many days old the given time stamp is
def howOldDays(timestamp:int) -> int:
    return howOld(timestamp).days