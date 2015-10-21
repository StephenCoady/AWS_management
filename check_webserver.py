#!/usr/bin/python3

# A program to check whether nginx is running on a linux instance
# Stephen Coady
# 20064122

import subprocess
import os
cmd = 'ps -A | grep nginx'
(status, output) = subprocess.getstatusoutput(cmd)

def nginx_check():
    if (status > 0):
      print("NOT RUNNING")
      response = input('Would you like to start the nginx server? (y/n) ')
      if response == 'y':
        os.system('sudo service nginx start')
    else:
      print("RUNNING")


# Define a main() function.
def main():
  nginx_check()
  
# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()