#!/bin/bash
#
# @Copyright: Mirantis 2013-JUL-17
# @author: awoodward
# @desc: master function for building entire node set
#

[ -z $PP_JOB ] && PP_JOB="ad-hoc"
[ -z $PP_JOBNUM ] && PP_JOBNUM=`dnorm`
export PP_JOB
export PP_JOBNUM

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

semiserial () {
  start=`dusec`
  logf "$0 started"
  ./bootstrap-node.sh $n1 $ni1 &
  ./bootstrap-node.sh $n2 $ni2 &
  ./bootstrap-node.sh $n3 $ni3 
  ssh ${SSHOPTS} root@$ni1 <ruby191.sh
  ssh ${SSHOPTS} root@$ni2 <ruby191.sh &
  ssh ${SSHOPTS} root@$ni3 <ruby191.sh &
  #./agent-run.sh $ni1 $ni2 $ni3 $ni1
  end=`dusec`
  logf "$0 ended in $(fexpr $end - $start)"
}

tear_down () {
  virsh destroy $n1
  virsh destroy $n2
  virsh destroy $n3
  #restart puppet services on pm_node, this will help prevent deadlocked 
  # pm_node
  ssh root@${PMNODE} <<EOF
/etc/init.d/thin stop
/etc/init.d/nginx stop
/etc/init.d/puppetdb stop
sleep 10
/etc/init.d/thin start
/etc/init.d/nginx start
/etc/init.d/puppetdb start
sleep 10
EOF
}

debug () {
  echo dusec `dusec`
  echo dnorm `dnorm`
  echo logpath $PP_LOGPATH
  set
}

#debug
tear_down
semiserial
