performance testing
===================

While this project is targeted around performance testing puppet manafests,
It is possible to use this framework to measure performance of any logged activity.

logging task output
-------------------

In the simplest form, you can take unixtime (EPOC) timestamps and put them infornt of some log lines simply you can:

    command | gawk '//  {print system("echo -n `date +%s.%N`"), $0; } END {print system("echo -n `date +%s.%N` _GAS_")}' >logfile

Alternatly, you can source scripts/functions.sh and use log which simply wraps the command with the above gawk satement

    log command > logfile


manual reporting
----------------
Once you have a one or more time stampped logfiles you can run the basic report engine on it. This will use a series of defaults which will create a report based on the contents of the current directory, using a regex intented for puppet. changing the exp_eval to your needs will change the blocking parser to fit you needs

    cd logs
    ../src/parser/agent.py


###Notes on rebuilding machines all the time

while the build scripts provided will attempt to erase the host keys for you 
(and bypass them with options passed to ssh) if they are allways from a 
trusted address range, you might want to disable host key checking in 
~/.ssh/config. This will help prevent issues with sometimes having the wrong 
key inserted in to your known hosts file.

    Host 192.168.0.*
       StrictHostKeyChecking no
       UserKnownHostsFile=/dev/null

###Random notes that are usually meaningless.


virsh change-media fuel-pm hdc --source /home/andreww/git/fuel/iso/build/iso/fuel-centos-6.4-x86_64-3.0.1.iso --insert --config
change-media fuel-pm hdc --eject --config