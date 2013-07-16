'''
Created on Jul 15, 2013

@author: andreww
'''

import re


#regex from https://github.com/rodjek/puppet-profiler/blob/master/lib/puppet-profiler.rb
exp_eval = re.compile("info: .*([A-Z][^\[]+)\[(.+?)\]: Evaluated in ([\d\.]+) seconds$")

def eval_capture(line, exp=exp_eval):
    ret = re.search(exp, line)
    return ret

sorted = "m.sort(lambda x,y: cmp(float(x[2]), float(y[2])))"
desc = lambda x,y: cmp(float(x[2]), float(y[2]))
asc = lambda x,y: cmp(float(y[2]), float(x[2]))


def group_results(results):
    ret = {}
    for item in results:
        if ret.has_key(item[0]):
            ret[item[0]].append(item)
        else:
            ret[item[0]] = [item,]
    for k, v in ret.iteritems():
        v.sort(asc)
    return ret

def print_results(results, mtime=50, sublist=10):
    ret = group_results(results)
    group_times = {}
    for k,v in ret.iteritems():
        group_times[k] = sum([float(item[2]) for item in v ])
    items = group_times.items()
    items.sort(lambda x,y: cmp(y[1],x[1]))
    print "showing up to %d executions where functions total \\\
    runtime exceeds %ds" %(sublist, mtime)
    print "total execution: %fs" %(sum(group_times.values()))
    for k,v in items:
        
        print "%s spent a total of %fs called %d avg %fs" %(k, v, len(ret[k]), v/len(ret[k]))
        if v < mtime:
            continue
        else:
            print "\t most expensive:"
            for parts in ret[k][:sublist]:
                print "\t" + str(parts)



def parse(ofile):
    m = [eval_capture(line).groups() for line in open(ofile, "r") if eval_capture(line) is not None]
    print_results(m)
    return m

ofile = "../puppet-agent-20130715_1005"

