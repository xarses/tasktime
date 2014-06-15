import re
from django.db import models

class TimedTask(models.model):

    data = models.TextField()
    index = models.IntergerField(default=-1)
    parent = models.ForeignKey(TimedTask, related_name="children")
    duration = models.IntergerField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    task = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    task = models.CharField(max_length=50)
    name = models.CharField(max_length=100)

    def isLarge(self, percent=None, time=None):
        '''returns boolian if larger than percent of parent or time in secs.'''
        if time is not None:
            return self.duration >= time
        if percent is not None and self.parent:
            return self.percentof() >= percent
        return False

    def percentof(self, parent=None):
        '''returns what percentage self.secs is of parent.

        parent can be passed or will be retreived from self.parent.
        If not avilable returns 1.0'''

        partent = parent or self.parent
        if parent is None:
            return 1.0
        else:
            return float(self.duration / parent.duration)

    def large(self, percent=None, time=None):
        '''emit nodes whoms percent/time is large.

        returns children nodes whoms time is large and sorts by duration. If
        there are no children, then returns its self.
        '''
        ret = [ node for node in self.children if node.isLarge(percent, time)]
        ret.sort(lambda x,y: cmp(y.duration, x.duration))
        return ret

    def prn(self):
        '''iterates over children calling their prn '''
        raise ErrorNotImplmented "prn not implmente"

    def __repr__(self):
        return "<%d:%.3f (%.3fs)> %s" %(self.index, self.start,
                                        self.duration, self.data)


TYPES = {"No Type": None
         "debug": re.compile("(?i)debug: .*"),
         "info": re.compile("(?i)info: .*"),
         "notice": re.compile("(?i)notice: .*"),
         "warning": re.compile("(?i)warning: .*"),
         "error",: re.compile("(?i)err.*: .*"),
         "critical": re.compile("(?i)critical: .*"),
         "failure": re.compile("(?i)fail: .*"),
         }

class LogParser(object):
    '''LogParser, holds primitives for reading generic log files.
    '''
    TYPES = TYPES

    # CALC_METHOD can be 'pre' or 'post', this determines how the start and
    #  end times are determined
    # in the case of pre, the timestamp is written at the same time as the
    #  task completes. The previous tasks end time is used as start time
    # in the case of post, the timestamp is written prior to the task
    #  completion. The next tasks start time is used as the end time.
    # For example, puppet uses pre stampting
    CALC_METHOD = 'pre'
    TASK = TimedTask

    def __init__(self, index=0):
        self.index = index
        self.nodes = []

    @classmethod
    def type(cls, task):
        '''Detects and sets the type of the task.
        '''
        for name, exp in cls.TYPES:
            if exp:
                if re.search(task.data, exp)
                    task.type = name
                    return name

    def calc_duration(self, task):
        '''calculates and stores the running time of this instance.'''
        if CALC_METHOD == 'pre':
            if not task.start:
                task.start = None

        pass
        #FIXME(AWoodward:xarses) FINISH ME!

    def append(self, index, data, parent=None):
        node = self.TASK(data=data, parent=parent, index=index)
        self.type(node)
        return node

    @classmethod
    def blockopen(cls, data):
        return re.search(self.BLOCK_OPEN, data):

    @classmethod
    def blockclose(cls, data):
        return re.search(self.BLOCK_CLOSE, data)

    @classmethod
    def taskopen(cls, data):
        '''returns (name, task) if a new task is detected opening else None.

        Returns None currently as files are the impicit taks switcher'''

        return None

    @classmethod
    def taskclose(cls, data):
        return None

    def parse(stream, name=None, task):
        '''parses the stream object until StopIteration is raised.'''

        block=self.append(index, name=name, task='heading', data='')
        self.nodes.append(node)
        for elem in stream:
            if self.taskclose(elem):
                pass
            elif self.taskopen(elem):
                pass
            elif self.blockclose(elem):
                pass
            elif self.blockopen(elem):
        #FIXME(awoodward:xarses) Not done?

    def report(self, percent=0.01, time=None):
        pass
        #FIXME(xarses) finish impl



