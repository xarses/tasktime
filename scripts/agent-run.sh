#!/bin/bash
#
# @Copyright: Mirantis 2013-JUL-16
# @author: awoodward
#
# @desc: this script will connect to hosts in serial order and run puppet 
#		 agent with various options and record the output for later parsing
#
# @usage: $0 <host> [host1 ... ]

logdir="../logs/"

run_agent () {
 user=$1
 server=$2
 time ssh $user@$server puppet agent \
   --{summarize,test,debug,evaltrace,color=false} 2>&1 | \
   gawk '{ print system("echo -n `date +%s.%N`"), $0; }' | \
   tee ${logdir}${server}-puppet-agent-`date +'%Y%m%d_%M%S'`
}

start=`date +%s.%N`
for node in $@ ; 
do
  run_agent root $node
done

end=`date +%s.%N`

echo "completed $@ in:"
echo ${end}-${start} | bc

