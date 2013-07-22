import re
from os import listdir

exp_base = "^([\d\.]+) ([\w]): .*([A-Z][^\[]+)\[(.+?)\]: (.*)$"
#           timestamp, log_type, func,          title,   eol

#regex from https://github.com/rodjek/puppet-profiler/blockob/master/lib/puppet-profiler.rb
exp_eval = re.compile("info: .*([A-Z][^\[]+)\[(.+?)\]: Evaluated in ([\d\.]+) seconds$")
exp_eval2 = re.compile("info: .*([A-Z][^\[]+)\[(.+?)\]: Evaluated in ([\d\.]+) seconds$")
desc = lambda x,y: cmp(float(x[2]), float(y[2]))
asc = lambda x,y: cmp(float(y[2]), float(x[2]))

def ldir(path="."):
    return listdir(path)

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
    
    def append(self, line):
        self.lines.append(line)
        if len(self.lines) == 1:
            self.stime = float(line.split("")[0])

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

    def append(self, block=None):
        """appends an object to the list, if no object is passed, will emit
        a new object from the classes constructor. If self._last has _calctime
        will run _last._calctime() before setting to new object in the stack.
        """
        if block is None:
            new = True
            block = self.constructor()
        if self._last is not None and hasattr(self._last, "_calctime"):
            self._last._calctime()
        block.parent = self
        self._last = block
        self.blocks.append(block)
        if new:
            return block

class JobLog(object):
    def __init__(self, model, path):
        self.model = model

def parse(ofile, exp=exp_eval):
    events = TaskLog(ofile)
    block = events.append()
    for line in open(ofile, "r"):
        if len(events) == 1:
            result = re.search("info: .*([A-Z][^\[]+)\[(.+?)\]: Starting to evaluate the resource$", line)
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
    events._calctime()
    return events
