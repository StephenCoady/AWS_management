#!/usr/bin/python3

# A program to run a new instance on AWS
# will also perform several tasks and maintenance functions
# Stephen Coady
# 20064122

import boto
import boto.ec2
import time
import subprocess

instance_name = 'GA_StephenCoady'
private_key_name = 'stephencoady'
conn = boto.ec2.connect_to_region('eu-west-1')
reservation = None
instance = None
start_time = time.time()

def new_server():
  print('Starting instance. This may take a moment.')
  conn = boto.ec2.connect_to_region('eu-west-1')
  global reservation 
  reservation = conn.run_instances('ami-69b9941e', key_name = private_key_name, instance_type = 't2.micro', security_groups = ['witsshrdp'])
  global instance 
  instance = reservation.instances[0]
  instance.add_tag('Name', instance_name)
  instance.update()

  print('Starting instance. This may take a moment.')
  while instance.state != 'running' :
    time.sleep(2)
    instance.update()

  print("Running!")


def terminate_server():
  if reservation == None :
    print("Sorry, it doesn't seem like you started any instances yet! Please create one.")
    answer = input("Would you like to see other instances you have running? (y/n) ")
    if answer == 'y' :
      view_all_instances()
  else :
    if len(reservation.instances) > 0 :
      for x in range(0, len(reservation.instances)) :
        print(str(x) + ": " + str(reservation.instances[x]))
        decision = input("Would you like to terminate one of these servers? (y/n) ")
        if decision == 'y' :
          number = input("Please enter the number of the instance you wish to terminate: ")
          if int(number) < len(reservation.instances) :
            reservation.instances[int(number)].terminate()
            print("Successfully terminated")
  

def install_nginx():
  if reservation == None :
    print("Sorry, it doesn't seem like you started any instances yet! Please create one.")
  else :
    if (time.time() - start_time) > 90 :
      print("Installing nginx...")
      dns = reservation.instances[0].public_dns_name
      command = "ssh -t -o StrictHostKeyChecking=no -i stephencoady.pem ec2-user@" + dns + " 'sudo yum -y install nginx'"
      (status, output) = subprocess.getstatusoutput(command)
      print(output)
    else :
      print("It doesn't look like the SSH service is started yet. Please wait. ")
      while (time.time() - start_time) < 90 :
        time.sleep(10)
        print("...")
      install_nginx()
  

def view_all_instances():
  reservations = conn.get_all_instances()
  instances = []
  for r in reservations:
    instances.extend(r.instances)

  my_instances = []
  for x in instances:
    if x.key_name == private_key_name :
      my_instances.append(x)

  for i in range (0, len(my_instances)) :
    print(str(i) + ": " + my_instances[i].tags["Name"] + " " + my_instances[i].state)
  

def copy_web_script():
  if reservation == None :
    print("Sorry, it doesn't seem like you started any instances yet! Please create one.")
  else :
    if (time.time() - start_time) > 90 :
      print("Copying script...")
      dns = reservation.instances[0].public_dns_name
      command = "scp -i stephencoady.pem check_webserver.py ec2-user@" + dns + ":"
      (status, output) = subprocess.getstatusoutput(command)
      print(output)
      print("Current directory: ")
      ls = "ssh -t -o StrictHostKeyChecking=no -i stephencoady.pem ec2-user@" + dns + " 'ls'"
      (status, output) = subprocess.getstatusoutput(ls)
      print(output)
      permission = "ssh -t -o StrictHostKeyChecking=no -i stephencoady.pem ec2-user@" + dns + \
      " 'chmod 700 check_webserver.py'"
      install_python()
    else :
      print("It doesn't look like the SSH service is started yet. Please wait. ")
      while (time.time() - start_time) < 90 :
        time.sleep(10)
        print("...")
      copy_web_script()

def install_python():
  dns = reservation.instances[0].public_dns_name
  py = "ssh -t -o StrictHostKeyChecking=no -i stephencoady.pem ec2-user@" + dns + " 'sudo yum -y install python34'"
  (status, output) = subprocess.getstatusoutput(py)
  print(output)

# Define a main() function.
def main():
  decision = None
  while decision != '0':
    print('')
    print('|==============================================|')
    print('|                  Main Menu                   |')
    print('|==============================================|')
    print('| 1) Create instance                           |')
    print('| 2) Terminate instance                        |')
    print('| 3) Install nginx                             |')
    print('| 4) View a list of instances created by you   |')
    print('| 5) Copy check_webserver script to instance   |')
    print('| 0) Exit                                      |')
    print('|______________________________________________|')
    print('')
    decision = input("Please enter your choice >>> ")
    if decision == '1':
      new_server()
    if decision == '2':
      terminate_server()
    if decision =='3':
      install_nginx()
    if decision =='4':
      view_all_instances()
    if decision =='5':
      copy_web_script()
  print("Exiting, cya!")
# main method
if __name__ == '__main__':
  main()