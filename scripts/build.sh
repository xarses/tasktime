#!/bin/bash
#
# @Copyright: Mirantis 2013-JUL-17
# @author: awoodward
# @desc: master function for building entire node set
#

source functions.sh

n1=fuel-controller-01
ni1=10.0.0.101
n2=fuel-controller-02
ni2=10.0.0.102
n3=fuel-controller-03
ni3=10.0.0.103


serial () {
  start=`dusec`
  logf "$0 started"
  ./bootstrap-node.sh $n1 $ni1
  ./bootstrap-node.sh $n2 $ni2
  ./bootstrap-node.sh $n3 $ni3
  ./agent-run.sh $ni1 $ni2 $ni3 $ni1
  end=`dusec`
  logf "$0 ended in $(fexpr $end - $start)"
}

tear_down () {
  virsh destroy $n1
  virsh destroy $n2
  virsh destroy $n3
}


tear_down
serial