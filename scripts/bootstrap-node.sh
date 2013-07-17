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
retry=1
user=root
domain=localdomain
pm_node=10.0.0.100

instance=$1
server=$2
destroy=$3

if [ "$destroy" == "destroy" ] ; then
	echo "destroying instance"
	virsh destroy $instance
fi

ssh_connect () {
while true
do
  ssh ${SSHOPTS} \
      $user@$server -C 'echo $HOSTNAME' 2>/dev/null
  [[ $? -eq 0 ]] && return 0
  #echo NOT connected to [${server}] sleeping for $retry...
  sleep $retry
done
}

if [[ "$server" != "$pm_node" ]] ; then
	echo "cleaning local ssh"
	ssh-keygen -f ~/.ssh/known_hosts -R ${server}
	ssh-keygen -f ~/.ssh/known_hosts -R ${instance}
	ssh-keygen -f ~/.ssh/known_hosts -R ${instance}.${domain}
	echo "cleaning master"
	ssh root@${pm_node} "/usr/bin/puppet cert clean ${instance}.${domain}"
	ssh root@${pm_node} "/usr/bin/cobbler system edit --name ${instance} \
		--netboot-enabled True"
fi


start=`date +%s.%N`
logf "$0 starting $instance"
$virsh start $instance
virt-viewer $instance & 

ssh_connect

end=`date +%s.%N`

logf "$0 done with $instance in $(fexpr ${end} - ${start})"


