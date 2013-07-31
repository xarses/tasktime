import re
from os import listdir
from string import join

exp_base = "^([\d\.]+) ([\w]): .*([A-Z][^\[]+)\[(.+?)\]: (.*)$"
#           timestamp, log_type, func,          title,   eol

#regex from https://github.com/rodjek/puppet-profiler/blockob/master/lib/puppet-profiler.rb
exp_eval = re.compile("[I,i]nfo: .*([A-Z][^\[]+)\[(.+?)\]: Evaluated in ([\d\.]+) seconds$")
exp_eval2 = re.compile("info: .*([A-Z][^\[]+)\[(.+?)\]: Evaluated in ([\d\.]+) seconds$")

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
    '''Line
    A Line object represents a line of text and should have been passed with
    a proceeding timestamp as unixtime (EPOCH). index is used for some ordering
    functions and calculating time duration (as compared to another index 
    from parent).
    '''
    def __init__(self, line, index=-1, parent=None, end=False, splitter=" "):
        split = line.split(splitter)
        self.utime = float(split.pop(0))
        self.line = join(split, splitter)
        self.dur = -1
        self.parent = parent
        self.index = index
        self.end = end
        self.type = 0
        if self.line == "_GAS_0\n":
            #This is a fix to be compatible with some old log files
            self.utime = parent.lines[index-1].utime
            self.end = True
            self.dur = 0
    
    def _type(self):
        """attemps to detect message line type"""
        for num, exp in TYPE_EXP:
            if exp:
                result = re.search(self.line, exp)
                if result is not None:
                    self.type = num
        
    def _calc(self):
        if self.parent is None:
            return
        if self.end:
            self.dur = 0
            return
        index = self.index + 1
        if index >= (len(self.parent.lines) - 1):
            nextline = self.parent.lines[index]
            self.dur = nextline.utime - self.utime
    
    def islarge(self, percent=None, time=None):
        '''islarge(percent=None, time=None) -> returns true / false if this is 
        larger than percent or time.
        '''
        if time is not None:
            return self.dur >= time
        if percent is not None:
            return (self.dur / self.parent.secs) >= percent

    def __repr__(self):
        return "<%d:%.3f (%.3fs)> %s" %(self.index, 
                                        self.utime, 
                                        self.dur, 
                                        self.line)

class Block(object):
    '''Block
    represents a block of text within a file that corrilates to a task.
    the parser will determine what a block should contain.
    a block will further contain Lines() that would each contain timestamps
    and data these are then processed to determine the amount of time that the
    block took to execute
    '''
    def __init__(self, index=-1, parent=None):
        self.index = index
        self.lines = []
        self.event = None
        self.func = None
        self.match = None
        self.secs = -1
        self.stime = -1
        self.etime = -1
        self.parent = parent
        self._last = None
        
    def __repr__(self):
        return "<%s[%s]> (%.2fs|%dl)" %(self.event, 
                                        self.func, 
                                        self.secs, 
                                        len(self.lines))
    def percentof(self, parent=None):
        '''percentof(parent=None) -> returns what percentage self.secs is of parent.
        parent can be passed or will be retreived from self.parent. If not avilable 
        returns 1.0
        '''  
        parent = parent or self.parent
        if parent is None:
            return 1.0
        else:
            return self.secs / parent.secs
        
    _conv = conv_utime_elapsec
    
    def _calc(self):
        if self.etime == -1: 
            if self.lines[-1].utime != -1:
                self.etime=self.lines[-1].utime
            else:
                self.etime=self.lines[-2].utime
        if self.stime == -1:
            self.stime = self.lines[0].utime
        self.secs=self.etime - self.stime
        return
    
    def prn(self):
        '''prn() -> iterates over every line in the block and prints its
        if it has strip, it strips it first
        '''
        for line in self.lines:
            if hasattr(line, 'strip'):
                line.strip()
            print line
    
    def large(self, percent=None, time=None):
        return [line for line in self.lines if line.islarge(percent, time)]

    def islarge(self, percent=None, time=None):
        '''islarge(percent=None, time=None) -> returns true / false if this is 
        larger than percent or time.
        '''
        if time is not None:
            return self.secs >= time
        if percent is not None:
            return self.percentof() >= percent
    
    def append(self, line):
        lindex = len(self.lines)
        lif = Line(line, lindex, self)
        self.lines.append(lif)
        if self._last:
            self._last._calc()
        self._last = lif
    
    def end(self):
        if self._last is not None:
            self._last.end = True
            self._last._calc()
            self.etime = self._last.utime
            self._calc()
        else:
            self.secs=-404
        return

class TaskLog(object):
    def __init__(self, name, node=None, task=None, etime=-1, constructor=Block):
        self.name = name
        self.node = node or name.split('-')[0]
        self.blocks = []
        self.task = task
        self.constructor = constructor
        self.etime = etime 
        self.secs = -1
        self._last = None
    
    def _calc(self):
        begin = self.blocks[0]
        if begin.secs == -1:
            begin._calc()
        end = self.blocks[-1]
        if end.secs == -1:
            end._calc()
        self.secs = end.etime - begin.stime
    
    def __repr__(self):
        return "<%s> (%.2f)" %(self.name, self.secs)

    def __len__(self):
        return self.blocks.__len__()    

    def summ(self, percent=None, time=None):
        events = [ item.event for item in self.blocks if item.event is not None]
        events = list(set(events))
        times = {}
        for event in events:
            times[event] = {'time': sum([item.secs for item in self.blocks 
                                        if item.event == event]),
                            'items': [item for item in self.blocks 
                                        if item.event == event 
                                        and item.islarge(percent, time)
                                     ],
                            }
            
        events.sort(lambda y,x: cmp(times[x]["time"], times[y]["time"]))
        #return events, times
        def islarge(num):
            if time is not None:
                return num >= time
            if percent is not None:
                return (num / self.secs) >= percent
        
        for event in events:
            if islarge(times[event]["time"]):
                print event
                for item in time[event]['items']:
                    print "%.3f %s" % (item.percentof(), item)
        
    def large(self, percent=None, time=None):
        nodes = [item for item in self.blocks if item.islarge(percent, time)]
        nodes.sort(lambda y,x: cmp(x.secs, y.secs))
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
        self.secs = -1

    def __repr__(self):
        return "<%s> tasks: %d, time: %.3f" %(self.model, 
                                              len(self.tasks), 
                                              self.secs)
    
    def _calc(self):
        self.secs = sum([item.secs for item in self.tasks if hasattr(item, "secs")])
    
    def append(self, item):
        self.tasks.append(item)

def loaddir(model, path='.'):
    files = listdir(path)
    job = JobLog(model, path)
    for ofile in files:
        job.append(parse(path + "/" + ofile))
    job._calc()
    job.tasks.sort(lambda x,y: cmp(x.blocks[0].stime, y.blocks[0].stime))
    return job

def report(job, percent=0.01, time=None):
    print "total runtime: %.2f" %job.secs
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
        block.append(line)
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

if __name__ == "__main__":
    job = loaddir('.')
    report(job)

