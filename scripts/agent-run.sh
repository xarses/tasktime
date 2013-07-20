#!/bin/bash
#
# @Copyright: Mirantis 2013-JUL-16
# @author: awoodward
#
# @desc: this script will connect to hosts in serial order and run puppet 
#	 agent with various options and record the output for later parsing
#
# @usage: $0 <host> [host1 ... ]

source functions.sh
logdir=${LOGBASE}`dnorm`/
mkdir -p $logdir

run_agent () {
 user=$1
 server=$2
 time ssh ${SSHOPTS} $user@$server puppet agent \
   --{summarize,test,debug,evaltrace,color=false} 2>&1 | \
   gawk '//  {print system("echo -n `date +%s.%N`"), $0; }  
         END {print system("echo -n `date +%s.%N` _GAS_")}' | \
   tee ${logdir}${server}-puppet-agent-`dnorm`
}

start=`dusec`

for node in $@ ; 
do
  istart=`dusec`
  logf "$0 started $node"
  run_agent root $node
  iend=`dusec`
  logf "$0 ended $node in $(fexpr $iend - $istart)"
done

end=`dusec`

logf "$0 completed $@ in: $(fexpr ${end} - ${start})"