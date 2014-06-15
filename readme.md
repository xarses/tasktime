========================
TaskTime logging runtime
========================

TaskTime is designed around recording the amount of time that something takes
to execute.

But wait, there are a lot of time routines out there, what makes this special?

TaskTime adds flexibility
* able to read already timestamped logs
* able to form task hierarchy allowing for detailed reporting

logging task output
-------------------

In the simplest form, you can take unixtime (EPOC) timestamps and put them
in front of some log lines simply you can:

    command | gawk '//  {print system("echo -n `date +%s.%N`"), $0; } END {print system("echo -n `date +%s.%N` _GAS_")}' >logfile

Alternately, you can source scripts/functions.sh and use log which simply wraps the command with the above gawk satement

    log command > logfile


manual reporting
----------------

Once you have a one or more time stamped log files you can run the basic report engine on it. This will use a series of defaults which will create a report based on the contents of the current directory, using a regex intented for puppet. changing the exp_eval to your needs will change the blocking parser to fit you needs

    cd logs
    ../src/parser/agent.py
