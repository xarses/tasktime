from django.db import models

# Create your models here.

class TaskLog(models.Model):
    name = models.TextField(max_length=90)
    node = models.TextField(max_length=50)
    #blocks from Block.parent
    task = None #not used in agent
    secs = models.FloatField()

class Block(models.Model):
    parent = models.ForeignKey(TaskLog, related_name='blocks')
    index = models.IntegerField()
    event = models.TextField(max_length=50)
    func = models.TextField(max_length=50)
    match = models.TextField(max_length=255)
    secs = models.FloatField()
    stime = models.FloatField()
    etime = models.FloatField()

class Line(models.Model):
    parent = models.ForeignKey(Block, related_name="lines")
    line = models.IntegerField()
    dur = models.FloatField()
    index = models.IntegerField()
    end = models.BooleanField(default=False)
    type = None  #Todo need to define
    utime = models.FloatField()

class JobLog(models.Model):
    pass