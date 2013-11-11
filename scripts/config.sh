#!/bin/bash
#
# @copyright: Mirantis 2013-JUL-17
# @author: awoodward
# @desc: config file
#


#LOGBASE is the base path for log files, and should allways contain a tailing /
LOGBASE="../logs/"

#BATCHLOG is the file used for all outter log messages and timings from scripts
# and is usually used from function.sh:logf
BATCHLOG=${LOGBASE}/batch.log

#
SSHOPTS="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "

PMNODE=10.0.0.100