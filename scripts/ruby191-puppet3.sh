#!/bin/bash

wget https://get.rvm.io/
chmod +x rvm-installer
./rvm-installer --ruby=1.9.3
echo
source /usr/local/rvm/scripts/rvm
rvm use default
ruby -rrbconfig -e 'puts RbConfig::CONFIG["CFLAGS"]'

time ruby -e "count = 0; while(count < 100000000); count = count + 1; end; puts count"


gem install json stomp systemu ruby-shadow
gem install puppet
gem install facter
yum -y install augeas-devel
gem install ruby-augeas
rvm autolibs packages
rvm reinstall ruby-1.9.3
rvm use default

