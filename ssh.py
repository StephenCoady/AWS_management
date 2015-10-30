# This helper module will connect to an Amazon instance using SSH
# Stephen Coady
# 20064122

import subprocess

def connect(dns, key, cmd):
    command = "ssh -t -o StrictHostKeyChecking=no -i " + key + ".pem ec2-user@" + dns + " " + cmd
    (status, output) = subprocess.getstatusoutput(command)
    return (status, output)

# does not use -t. the advantage of this is for simple commands it will not print
# that the connection is closed
def connect_no_terminal(dns, key, cmd):
  command = "ssh -o StrictHostKeyChecking=no -i " + key + ".pem ec2-user@" + dns + " " + cmd
  (status, output) = subprocess.getstatusoutput(command)
  return (status, output)

def copy(dns, key, file, dest):
  command = "scp -i " + key + ".pem " + file + " " + "ec2-user@" + dns + ":" + dest
  (status, output) = subprocess.getstatusoutput(command)
  return (status, output)
