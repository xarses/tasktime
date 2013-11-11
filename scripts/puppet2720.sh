#!/bin/bash
#
# @Copyright: Mirantis 2013-JUL-24
# @author: awoodward
# @desc: This snippit will install rvm and puppet 2.7.20
#


wget -O rvm-installer https://get.rvm.io/
chmod +x rvm-installer
./rvm-installer --ruby=system
 
echo "forced space"
source /usr/local/rvm/scripts/rvm

gem install --version '<2.7.21' puppet