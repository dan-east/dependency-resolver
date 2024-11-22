import signal
import time
import logging

_logger = logging.getLogger(__name__) # module name

# Keeps this python process alive by going into an infinite sleep-loop.
# Parameters:
#   sleep - number of seconds to sleep per loop
def keepAlive(sleep:int = 5) :
    _logger.debug("Going into an infinite loop...")
    while 1 :
        time.sleep(sleep)
    _logger.debug("...exiting loop.")


# Respond to signals indicating shutdown (for example ctrl-c)
#  Useful when keeping this python process alive.
# Parameters:
#   function - a function to call when a shutdown signal is received
def setStopSignals(func) :
    signal.signal(signal.SIGTERM, func)
    signal.signal(signal.SIGHUP, func)
    signal.signal(signal.SIGINT, func)
    signal.signal(signal.SIGUSR1, func)
    signal.signal(signal.SIGUSR2, func)
    signal.signal(signal.SIGQUIT, func)


# Respond to signals indicating a child process has terminated.
# Parameters:
#   function - a function to call when a shutdown signal is received
def setChildStoppedSignal(func) :
    signal.signal(signal.SIGCHLD, func)
