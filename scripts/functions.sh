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
