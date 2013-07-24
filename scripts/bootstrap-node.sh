#!/bin/bash
#
# @Copyright: Mirantis 2013-JUL-13
# @author: awoodward
#
# @desc: this will call virsh and start node and attempt to capture start and
#        end times of bootstrap process. This is done by waiting for sucessful
#        ssh login. This requires GASSAPI disabled and a pre-populated 
#        authorized_keys inside of the ks scripts.
#
# @usage: $0 <instance name> <ip> [destroy]


source functions.sh

virsh=/usr/bin/virsh
ssh=/usr/bin/ssh
user=root
domain=localdomain

instance=$1
server=$2
destroy=$3

(
if [ "$destroy" == "destroy" ] ; then
	echo "destroying instance"
	virsh destroy $instance
fi

if [[ "$server" != "$pm_node" ]] ; then
	echo "cleaning local ssh"
	ssh-keygen -f ${HOME}/.ssh/known_hosts -R ${server}
	ssh-keygen -f ${HOME}/.ssh/known_hosts -R ${server}
	ssh-keygen -f ${HOME}/.ssh/known_hosts -R ${instance}
	ssh-keygen -f ${HOME}/.ssh/known_hosts -R ${instance}.${domain}
	echo "cleaning master"
	ssh root@${PMNODE} "puppet cert clean ${instance}.${domain}"
	ssh root@${PMNODE} "cobbler system edit --name ${instance} \
		--netboot-enabled True"
fi


start=`date +%s.%N`
logf "$0 starting $instance"
$virsh start $instance
#virt-viewer $instance &disown

ssh_connect $user $server 'echo $HOSTNAME' 2>/dev/null

end=`date +%s.%N`

logf "$0 done with $instance in $(fexpr ${end} - ${start})"

) 2>&1 | \
   gawk '//  {print system("echo -n `date +%s.%N`"), $0; }                              END {print system("echo -n `date +%s.%N` _GAS_")}' | \
   tee ${PP_LOGDIR}${server}-boot-strap-`dnorm`
