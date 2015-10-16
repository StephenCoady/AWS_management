#!/usr/bin/python3

# A program to run a new instance on AWS
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


def terminate_server():

  print(len(reservation.instances))

  for x in range(0, len(reservation.instances)) :
    print(str(x) + ": " + str(reservation.instances[x]))

def install_nginx():
  print(reservation.instances[0].public_dns_name)

# Define a main() function.
def main():
  decision = None
  while decision != 0:
    print('1) Create instance')
    print('2) Terminate instance')
    print('3) Install nginx')
    print('0) Exit')
    decision = input("Please enter your choice >>> ")
    if decision == '1':
      new_server()
    if decision == '2':
      terminate_server()
    if decision =='3':
      install_nginx()
    if decision == '0':
      exit()

  
# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()