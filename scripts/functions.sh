
#!/bin/bash
#
# @copyright: Mirantis 2013-JUL-17
# @author: awoodward
#
# @desc: helper functions
#

source config.sh

dusec () {
 date +%s.%N
}

dnorm () {
 date +%Y%m%d_%H%M
}

logf () {
  echo `dusec`: $@ | tee -a ${BATCHLOG} 
}

fexpr () {
  echo $@ | bc 2>/dev/null
}

log () {

 $@ 2>&1 | \
   gawk '//  {print system("echo -n `date +%s.%N`"), $0; }
         END {print system("echo -n `date +%s.%N` _GAS_")}'
}


ssh_connect () {
user=$1
host=$2
shift $((2))
command=${@}
while true
do
  ssh ${SSHOPTS} -l $user $host $command  
  [[ $? -eq 0 ]] && return 0
  #echo NOT connected to [${server}] sleeping for $retry...
  sleep 1
done
}

## leave at bottom
[ -z $PP_JOB ] && PP_JOB="ad-hoc"
[ -z $PP_JOBNUM ] && PP_JOBNUM=`dnorm`
PP_LOGDIR=${LOGBASE}/${PP_JOB}/${PP_JOBNUM}/
mkdir -p $PP_LOGDIR
