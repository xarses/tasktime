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
 date +%Y
}

logf () {
  echo `date +%s.%N`: $@ | tee -a ${BATCHLOG}
}

