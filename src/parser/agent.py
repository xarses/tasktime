import re

exp_base = "^([\d\.]+) ([\w]): .*([A-Z][^\[]+)\[(.+?)\]: (.*)$"
#           timestamp, log_type, func,          title,   eol

class logset(object):
    usec = 0.0
    def __init__(self, time, log_type, func, title, eol, usec=0.0, raw=None, 
                 addtl=None):
        self.time = float(time)
        self.type = log_type
        self.func = func
        self.title = title
        self.eol = eol
        self.raw = raw
        self.addtl = addtl
    __cmp__ = usec.__cmp__

def parse_line(line, logobj, exp=exp_base):
    obj = logobj(**re.search(exp, line))
    obj.raw = line
    return obj

def parse(handle, logobj=logset):
    last_log = parse_line(handle.next(), logobj)
    #next_log = parse_line(handle.readline())
    logs = [last_log, ]
    for line in handle:
        curr_log = parse_line(line, logobj)
        last_log.usec = curr_log.time - last_log.time
        logs.append(curr_log)
        last_log = curr_log
    return logs
