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
# @usage: $0 <instance name> <ip>

virsh=/usr/bin/virsh
ssh=/usr/bin/ssh
retry=1
user=root

instance=$1
server=$2


ssh_connect () {
while true
do
  ssh -o UserKnownHostsFile=/dev/null \
      -o StrictHostKeyChecking=no \
      $user@$server -C 'echo $HOSTNAME'
  [[ $? -eq 0 ]] && return 0
  echo NOT connected to [${server}] sleeping for $retry...
  sleep $retry
done
}


start=`date +%s.%N`

$virsh start $instance
virt-viewer $instance & 

ssh_connect

end=`date +%s.%N`

echo ${end}-${start} | bc


