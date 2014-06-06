from django.db import models

# Create your models here.

class Snip(models.Model):
    name = models.CharField(max_length=50)
    data = models.TextField()

class Task(models.Model):
    name = models.CharField(max_length=50)
    snips = models.ManyToManyField(Snip, related_name="+")
    
class Stage(models.Model):
    name = models.CharField(max_length=50)
    tasks = models.ManyToManyField(Task, related_name="stages")
    
class Profile(models.Model):
    name = models.CharField(max_length=50)
    stages = models.ManyToManyField(Stage, related_name="profiles")
    
class Job(models.Model):
    name = models.CharField(max_length=50)
    profile = models.ForeignKey(Profile, related_name="jobs")
    logpath = models.CharField(max_length=250)
    scheduled = None
    time_start = None
    time_end = None
    complete = None
    joblog = None #TODO: need to create relation to report engine
        

