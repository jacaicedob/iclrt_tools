#!/usr/bin/python

import subprocess
import signal
import os

processes = ["iclrt_check_", "status_v10", "send.pl"]

for process in processes:
	command = "ps -A | grep %s" % process
	proc = subprocess.Popen(command,shell=True, stdout=subprocess.PIPE)
	out, err = proc.communicate()
	
	for line in out.splitlines():
		if process in line:
			pid = int(line.split()[0])
			os.kill(pid, signal.SIGKILL)