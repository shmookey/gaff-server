'''compile.py -- Gaff world compiler'''

import sys
from datetime import datetime

class EventLogger (object):
    INFO    = 1000
    ERROR   = 1001
    WARNING = 1002
    DEBUG   = 1003
    ETYPES = {INFO:'INFO',ERROR:'ERROR',WARNING:'WARNING',DEBUG:'DEBUG'}
    
    def __init__ (self, info=[sys.stdout], error=[sys.stderr], warning=[sys.stderr], debug=[]):
        self.log = []
        self.outputs = {}
        self.outputs[EventLogger.INFO] = info
        self.outputs[EventLogger.ERROR] = error
        self.outputs[EventLogger.WARNING] = warning
        self.outputs[EventLogger.DEBUG] = debug

    def error (self, message):
        self.__log_event (EventLogger.ERROR, message)

    def info (self, message):
        self.__log_event (EventLogger.INFO, message)

    def warning (self, message):
        self.__log_event (EventLogger.WARNING, message)

    def debug (self, message):
        self.__log_event (EventLogger.DEBUG, message)

    def __log_event (self, etype, message):
        event = (datetime.now(), etype, message)
        self.log.append (event)
        outputs = self.outputs[etype]
        event_str = EventLogger.__format_event (event)
        for output in outputs:
            output.write('%s\n' % event_str)

    @classmethod
    def __format_event (cls, event):
        date = event[0].strftime('%Y-%m-%d %H:%M:%S')
        etype = EventLogger.ETYPES[event[1]]
        message = str(event[2])
        return '%s %s %s' % (date, etype, message)

