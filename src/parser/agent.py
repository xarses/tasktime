import re
from os import listdir
from string import join

exp_base = "^([\d\.]+) ([\w]): .*([A-Z][^\[]+)\[(.+?)\]: (.*)$"
#           timestamp, log_type, func,          title,   eol

#regex from https://github.com/rodjek/puppet-profiler/blockob/master/lib/puppet-profiler.rb
exp_eval = re.compile("[I,i]nfo: .*([A-Z][^\[]+)\[(.+?)\]: Evaluated in ([\d\.]+) seconds$")
exp_eval2 = re.compile("info: .*([A-Z][^\[]+)\[(.+?)\]: Evaluated in ([\d\.]+) seconds$")
desc = lambda x,y: cmp(float(x[2]), float(y[2]))
asc = lambda x,y: cmp(float(y[2]), float(x[2]))

TYPE_NAMES={0: "No Type",
            1: "debug",
            2: "info",
            3: "notice",
            4: "warning",
            5: "error",
            6: "critical",
            7: "failure",
            }

TYPE_EXP = {0: None,
            1: re.compile("(?i)debug: .*"),
            2: re.compile("(?i)info: .*"),
            3: re.compile("(?i)notice: .*"),
            4: re.compile("(?i)warning: .*"),
            5: re.compile("(?i)error: .*"),
            6: re.compile("(?i)critical: .*"),
            7: re.compile("(?i)fail: .*"),
            }

#These type numbers are considered errors for check error reporting.
TYPE_ISERROR = [4,5,6,7]

def ldir(path="."):
    return listdir(path)

def conv_utime_elapsec(block, percision=3):
    """converts unix time stamps in a block object to seconds elapsed
    percision defaults to 3 decimial places
    """
    def get_ts(line):
        return float(line.split(" ")[0])
    def replace_ts(line, ts):
        parts = line.split(" ")
        parts[0] = ts
        return join(parts, " ")
    total = 0.0
    cur = block.lines[0]
    cur_ts = get_ts(cur)
    for index in range(len(block.lines) ):
        if index + 1 >= len(block.lines):
            #trick out the last line to noop itself
            nex = cur
            nex_ts = cur_ts
        else:
            nex = block.lines[index + 1]
            nex_ts=get_ts(nex)
        rt = round(nex_ts - cur_ts, percision)
        ts = "%.3f (%.3fs)" % (total, rt)
        block.lines[index-1] = replace_ts(cur, ts)
        total += rt
        cur = nex
        cur_ts = nex_ts

class Line(object):
    def __init__(self, line, index=-1, parent=None, end=False):
        split = line.split(" ")
        self.time = float(split[0])
        self.line = join(split, " ")
        self.dur = -1
        self.parent = parent
        self.end = end
        self.type = 0
    
    def _type(self):
        """attemps to detect message line type"""
        for id, exp in TYPE_EXP:
            if exp:
                result = re.search(self.line, exp)
                if result is not None:
                    self.type = id
        
    def _calc(self):
        if self.parent is None:
            return
        if self.end:
            self.dur = 0
        index = self.index + 1
        if index >= len(self.parent.lines - 1):
            nextline = self.parent.lines[index]
            self.dur = nextline.time - self.time

class Block(object):
    def __init__(self, index=-1, parent=None):
        self.index = index
        self.lines = []
        self.event = None
        self.func = None
        self.match = None
        self.time = -1
        self.stime = 0
        self.etime = 0
        self.parent = parent
    
    def __repr__(self):
        return "<%s[%s]> (%.2fs|%dl)" %(self.event, 
                                        self.func, 
                                        self.time, 
                                        len(self.lines))
    def percentof(self, parent=None):
        parent = parent or self.parent
        if parent is None:
            return 100.0
        else:
            return self.time / parent.time
        
    _conv = conv_utime_elapsec
    
    def _calc(self):
        if not self.etime: 
            if self.lines[-1] == "_GAS_0\n":
                #This is needed for a bug to the last line in the log from an old rev of
                # agent-run.sh
                t2 = float(self.lines[-2].split(" ")[0])
            else:
                t2 = float(self.lines[-1].split(" ")[0])
        self.etime=t2
        if not self.stime:
            self.stime = float(self.lines[0].split(" ")[0])
        self.time=t2 - self.stime
        return
    
    def prn(self):
        for line in self.lines:
            line.strip()
            print line
    
    def large(self, percent=None, time=None):
        if time is not None:
            return self.time >= time
        if percent is not None:
            return self.percentof() >= percent
    
    def append(self, line):
        #self.lines.append(line)
        #if len(self.lines) == 1:
        #    self.stime = float(line.split("")[0])
        lindex = len(self.lines) - 1
        line = Line(line, lindex, self)
        self.lines.append(line)
        self._last._calc()
        self._last = line
    
    def end(self):
        self._last.end = True
        self._last._calc()
        self._calc()
    

class TaskLog(object):
    def __init__(self, name, node=None, task=None, etime=-1, constructor=Block):
        self.name = name
        self.node = node or name.split('-')[0]
        self.blocks = []
        self.task = task
        self.constructor = constructor
        self.etime = etime 
        self.time = -1
        self._last = None
    
    def _calc(self):
        begin = self.blocks[0]
        if begin.time == -1:
            begin._calc()
        end = self.blocks[-1]
        if end.time == -1:
            end._calc()
        self.time = end.etime - begin.stime
    
    def __repr__(self):
        return "<%s> (%.2f)" %(self.name, self.time)

    def __len__(self):
        return self.blocks.__len__()    

    def large(self, percent=None, time=None):
        nodes = [item for item in self.blocks if item.large(percent, time)]
        nodes.sort(lambda y,x: cmp(x.time, y.time))
        return nodes

    def append(self, block=None):
        """appends an object to the list, if no object is passed, will emit
        a new object from the classes constructor. If self._last has _calc
        will run _last._calc() before setting to new object in the stack.
        """
        if block is None:
            new = True
            block = self.constructor()
        if self._last is not None and hasattr(self._last, "end"):
            self._last.end()
        block.parent = self
        self._last = block
        self.blocks.append(block)
        block.index = len(self.blocks)
        if new:
            return block

class JobLog(object):
    def __init__(self, model, path):
        self.model = model
        self.path = path
        self.tasks = []
        self.time = -1

    def __repr__(self):
        return "<%s> tasks: %d, time: %.3f" %(self.model, 
                                              len(self.tasks), 
                                              self.time)
    
    def _calc(self):
        self.time = sum([item.time for item in self.tasks if hasattr(item, "time")])
    
    def append(self, item):
        self.tasks.append(item)

def loaddir(model, path='.'):
    files = listdir(path)
    job = JobLog(model, path)
    for ofile in files:
        job.append(parse(ofile))
    job._calc()
    job.tasks.sort(lambda x,y: cmp(x.blocks[0].stime, y.blocks[0].stime))
    return job

def report(job, percent=0.01, time=None):
    print "total runtime: %.2f" %job.time
    for task in job.tasks:
        print task
        for item in task.large(percent, time):
            print "%.3f: %s" %(item.percentof(), item)
        print "\n"

def parse(ofile, exp=exp_eval):
    events = TaskLog(ofile)
    block = events.append()
    for line in open(ofile, "r"):
        if len(events) == 1:
            result = re.search(exp, line)
            if result is not None:
                block.event = "pre-evaluates"
                block = events.append()
        block.lines.append(line)
        result = re.search(exp, line)
        if result is not None:
            block.match = result.groups()
            block.event = block.match[0]
            block.func = block.match[1]
            block = events.append()        
    if block.event is None:
        block.event = "post-evaluates"
    events._calc()
    return events
