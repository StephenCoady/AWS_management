#!/usr/bin/python3

# A program to run a new instance on AWS
# will also perform several tasks and maintenance functions
# Stephen Coady
# 20064122

import boto
import boto.ec2
import time

instance_name = 'GA_StephenCoady'
private_key_name = 'stephencoady'
conn = boto.ec2.connect_to_region('eu-west-1')
reservation = None
instance = None

def new_server():
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
    answer = input("Would you like to see other reservations you have running? (y/n) ")
    if answer == 'y' :
      reservations = conn.get_all_instances()
      instances = []
      for r in reservations:
        instances.extend(r.instances)

      my_instances = []
      for x in instances:
        if x.key_name == private_key_name :
          my_instances.append(x)

      for i in range (0, len(my_instances)) :
        print(my_instances[i])
  else :
    print(len(reservation.instances))

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
    print(reservation.instances[0].public_dns_name)

# Define a main() function.
def main():
  decision = None
  while decision != 0:
    print(' ')
    print('1) Create instance')
    print('2) Terminate instance')
    print('3) Install nginx')
    print('0) Exit')
    print(' ')
    decision = input("Please enter your choice >>> ")
    if decision == '1':
      new_server()
    if decision == '2':
      terminate_server()
    if decision =='3':
      install_nginx()
    if decision == '0':
      exit()

  
# main method
if __name__ == '__main__':
  main()