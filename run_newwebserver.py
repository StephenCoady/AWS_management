#!/usr/bin/python3

# A program to run a new instance on AWS
# will also perform several tasks and maintenance functions
# Stephen Coady
# 20064122

import boto
import boto.ec2
import time
import logger
import ssh
import menu
import subprocess
import os

private_key_name = None
conn = boto.ec2.connect_to_region('eu-west-1')
reservation = None
instance = None
my_instances = None
start_time = time.time()


def set_pem_key(pem_key):
  private_key_name = pem_key

def new_server():
  global reservation
  global instance
  print("Please enter the name you would like to call the instance,") 
  print("leave blank for the default.")
  instance_name = input(">>> ")
  if instance_name == "":
    instance_name = 'GA_StephenCoady'
  print('Starting instance. This may take a moment.')
  reservation = conn.run_instances('ami-69b9941e', key_name = private_key_name, instance_type = 't2.micro', security_groups = ['witsshrdp'])
  instance = reservation.instances[0]
  instance.add_tag('Name', instance_name)
  instance.update()

  while instance.state != 'running' :
    time.sleep(2)
    instance.update()

  print("\nRunning!")


def terminate_server():
  global instance
  try :
    if instance.state == 'terminated' :
      print('Instance already terminated!')
      logger.status_log("User tried to stop an instance already terminated")
    else :
      decision = input("Are you sure you wish to terminate this instance? (y/n) ")
      if decision == 'y':
        instance.terminate();
        print("Instance terminated!")
      else :
        print("Termination aborted! Instance is safe...for now.")
  except :
    logger.status_log("Error terminating instance: " + instance)

def start_server():
  global instance
  try :
    if instance.state == 'terminated':
      print("Sorry, this instance is terminated. RIP.")
    else :
      if instance.state == 'running' :
        print('Instance already running!')
        logger.status_log("User tried to start an instance already running")
      else :
        instance.start();
        print("Instance started!")
  except :
    logger.status_log("Error starting instance: " + instance)

def stop_server():
  global instance
  if running_check() :
    try :
      if instance.state == 'terminated':
        print("Sorry, this instance is terminated. RIP.")
      else :
        if instance.state == 'stopped' :
          print('Instance already stopped!')
          logger.status_log("User tried to stop an instance already stopped")
        else :
          instance.stop();
          print("Instance stopped!")
    except :
      logger.status_log("Error starting instance: " + instance)

def install_nginx():
  global instance
  if running_check() :
    if (time.time() - start_time) > 90 :
      print("Installing nginx...")
      dns = instance.public_dns_name
      (status, output) = ssh.connect(dns, "sudo yum -y install nginx")
      if status > 0:
        print("Something went wrong. Check error log for information.")
        logger.status_log("Can't install nging using SSH. Error message: ")
        logger.status_log(output)
      else : 
        print("Nginx successfully installed on instance.")
    else :
      print("It doesn't look like the SSH service is started yet. Please wait. ")
      logger.status_log("User tried to use SSH service when it was not ready.")
      while (time.time() - start_time) < 90 :
        time.sleep(10)
        print("...")
      install_nginx()


def view_all_instances():
  global my_instances

  reservations = conn.get_all_instances()
  instances = []
  for r in reservations:
    instances.extend(r.instances)

  my_instances = []
  for x in instances:
    if x.key_name == private_key_name :
      my_instances.append(x)

  if len(my_instances) == 0:
    print("No instances associated with this key. Please ensure it is the")
    print("correct key or that you have created some first.")
  else :
    print()
    print("No Name            Status  Time Started")
    print("---------------------------------------")
    for i in range (0, len(my_instances)) :
      print(str(i) + ": " + my_instances[i].tags["Name"] + " " + my_instances[i].state + " " + my_instances[i].launch_time)
    print("\n")

def copy_web_script():
  global instance
  if running_check() :
    if (time.time() - start_time) > 90 :
      print("Copying script...")
      dns = instance.public_dns_name
      
      (status, output) = ssh.copy(dns, "check_webserver.py")
      
      if status > 0:
        logger.status_log("Can't connect using ssh. Error message: ")
        logger.status_log(output)
        print("Something isn't quite right. Please try again.")
        return
      
      else :
        (status, output) = ssh.connect(dns, "ls")
        print("Current directory: ")
        print(output)
      
      (status, output) = ssh.connect(dns, "chmod 700 check_webserver.py")
    else :
      logger.status_log("SSH not ready. (copy_web_script())")
      print("Sorry, SSH doesn't seem to be running yet. Please wait while it starts.")
      while (time.time() - start_time) < 90 :
        time.sleep(10)
        print("...")
      copy_web_script()

def run_nginx_check():
  global instance
  if running_check() :
    dns = instance.public_dns_name
    (status, output) = ssh.connect(dns, "sudo python3 check_webserver.py")
    if "command not found" in output:
      print("It doesn't look like you've installed python, please try that first.")
    elif "No such file" in output:
      print("It doesn't look like you've copied the file to the instance, please try that first.")
    else :
      print(output)
      if status > 0 :
        choice = input("Would you like to start nginx? (y/n) ")
        if choice == 'y' :
          (stat, out) = ssh.connect(dns, "sudo service nginx start")
          if "unrecognized service" in out:
            print("It doesn't look like you've installed nginx, please try that first.")
          run_nginx_check()
        else :
          print("Nginx not started.")


def install_python():
  global instance
  if running_check() :
    dns = instance.public_dns_name
    (status, output) = ssh.connect(dns, "sudo yum -y install python34")
    if status == 0:
      print("Python installed successfully!")
    else :
      logger.status_log("Python not installed correctly.")
      try_again = input("Oops, something wen't wrong installing python. Try again? (y/n) ")
      if try_again == 'y':
        install_python()

def run_user_command():
  global instance
  if running_check():
    dns = instance.public_dns_name
    command = None
    print("Please use x to exit the python terminal. ")
    sudo = input("Would you like to emulate the terminal? (y/n) >>> ")
    while command != 'x':
      command = input("Please enter the command you wish to run, don't forget to include -y to accept changes if necessary >>> ")
      if command !='x':
        if sudo == 'y':
          cmd = "ssh -t -o StrictHostKeyChecking=no -i stephencoady.pem ec2-user@" + dns + " " + command
          print(os.system(cmd))
        else :
          cmd = "ssh -o StrictHostKeyChecking=no -i stephencoady.pem ec2-user@" + dns + " " + command
          print(os.system(cmd))

def visit_website():
  global instance
  if running_check():
    dns = instance.public_dns_name
    (status, output) = subprocess.getstatusoutput("curl " + dns)
    if "Connection refused" in output :
      print("Looks the nginx server isn't running. Please start it.")
      logger.status_log("Connection refused to " + dns + ". ")
    else :
      print(output)

def view_access_log():
  global instance
  if running_check():
    dns = instance.public_dns_name
    ssh.connect(dns, "sudo chmod 777 /var/log/nginx")
    cmd = "nano /var/log/nginx/access.log"
    command = "ssh -t -o StrictHostKeyChecking=no -i stephencoady.pem ec2-user@" + dns + " " + cmd
    print(os.system(command))

def view_error_log():
  global instance
  if running_check():
    dns = instance.public_dns_name
    ssh.connect(dns, "sudo chmod 777 /var/log/nginx")
    cmd = "nano /var/log/nginx/error.log"
    command = "ssh -t -o StrictHostKeyChecking=no -i stephencoady.pem ec2-user@" + dns + " " + cmd
    print(os.system(command))

def running_check():
  global instance
  if instance.state == 'running':
    return True
  else :
    print("Instance not running yet, please make sure it is running and then try again.")
    logger.status_log("User tried to access non-running instance.")
    return False

# Define a main() function.
def main():
  menu.start_menu()
  global private_key_name 
  print("Please enter key name, or leave blank for the default (stephencoady)")
  private_key_name = input(" >>> ")
  if private_key_name == "" :
    private_key_name = "stephencoady"
  decision = None
  submenu = None
  while decision != '0':
    menu.main_menu()
    submenu = None
    decision = input("Please enter your choice >>> ")
    if decision == '1':
      new_server()
    if decision == '2':
      print("Gathering information about your instances, please wait.")
      view_all_instances()
      global my_instances
      if my_instances != None :
        instance_choice = input("Please enter the number of the instance you wish to manage (x to cancel) >>> ")
      else :
        print("You have no instances, please create one first.")
      global instance
      if instance_choice != 'x' :
        instance = my_instances[int(instance_choice)]
        while submenu != '0':
          menu.instance_manager()
          submenu = input("Please enter your choice >>> ")
          if submenu == '1':
            start_server()
          if submenu == '2':
            stop_server()
          if submenu == '3':
            terminate_server()
          if submenu == '4':
            install_python()
          if submenu == '5':
            install_nginx()
          if submenu == '6':
            copy_web_script()
          if submenu == '7':
            run_nginx_check()
          if submenu == '8':
            run_user_command()
          if submenu == '9':
            visit_website()
          if submenu == '10':
            view_access_log()
          if submenu == '11':
            view_error_log()
  print("Exit called.")

if __name__ == '__main__':
  main()
