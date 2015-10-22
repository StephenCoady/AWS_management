#!/usr/bin/python3

# This class will connect to an Amazon instance using SSH
# Stephen Coady
# 20064122

import subprocess

def connect(dns, cmd):
  ls = "ssh -t -o StrictHostKeyChecking=no -i stephencoady.pem ec2-user@" + dns + " " + cmd
  (status, output) = subprocess.getstatusoutput(ls)
  return (status, output)

def copy(dns, file):
  command = "scp -i stephencoady.pem" + " " + file + " " + "ec2-user@" + dns + ":"
  (status, output) = subprocess.getstatusoutput(command)
  return (status, output)
