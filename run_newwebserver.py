#!/usr/bin/python3

# A program to manage a user's AWS. Uses the boto API to interact with AWS.
# Functions include creating, stopping and terminating a new instance
# managing your list of instances (obtained using your key as a search)
# installing nginx, python, and managing nginx
# 
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
import webbrowser

private_key_name = None
conn = boto.ec2.connect_to_region('eu-west-1')

# this variable is the current instance being worked on. can never be None. 
# once a new instance is called this is update or once one is selected from the list
instance = None
my_instances = None

# Method to create a new instance. 
# uses the user-defined key name to create an instance
def new_instance():
  global instance

  print("Please enter the name you would like to call the instance,") 
  print("leave blank for the default.")
  instance_name = input(">>> ")
  if instance_name == "":
    instance_name = 'GA_StephenCoady'
  print('Starting instance. This may take a moment.')
  try:
    # creates a temporary reservation to create an instance from
    reservation = conn.run_instances('ami-69b9941e', key_name = private_key_name, \
      instance_type = 't2.micro', security_groups = ['witsshrdp'])
    instance = reservation.instances[0]
    instance.add_tag('Name', instance_name)
    instance.update()

    while instance.state != 'running' :
      time.sleep(2)
      instance.update()

    print("\nRunning!")
  except Exception as e:
    error = str(e)
    print("Something went wrong. Please try again.")
    logger.status_log("new_server method failed. Error: " + error)

# terminates the current instance.
def terminate_instance():
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
  except Exception as e:
    error = str(e)
    print("Cannot terminate instance, something went wrong. Please try again.")
    logger.status_log("Error terminating instance. Error: " + error)

# starts the current instance
def start_instance():
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
  except Exception as e:
    error = str(e)
    print("Cannot start instance, something went wrong. Please try again.")
    logger.status_log("Error starting instance. Error: " + error)

# stops the current instance
def stop_instance():
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
    except Exception as e:
      error = str(e)
      print("Cannot stop instance, something went wrong. Please try again.")
      logger.status_log("Error stopping instance. Error: " + error)

# installs nginx on the current instance.
def install_nginx():
  global instance
  if running_check() :
    try :
        print("Installing nginx...")
        dns = instance.public_dns_name
        (status, output) = ssh.connect(dns, private_key_name, "sudo yum -y install nginx")
        if status > 0:
          print("Something went wrong. Check error log for information.")
          logger.status_log("Can't install nginx using SSH. Error message: ")
          logger.status_log(output)
        else : 
          print("Nginx successfully installed on instance.")
    except Exception as e:
      error = str(e)
      print("Something went wrong. Please try again.")
      logger.status_log("install_nginx method failed. Error: " + error)


# creates a list of all instances associated with the key the user entered.
def view_all_instances():
  global my_instances

  try :
    # loops through all reservations associated with this connection
    # and forms a list of instances
    reservations = conn.get_all_instances()
    instances = []
    for r in reservations:
      instances.extend(r.instances)

    # within these instances if the key name matches the user entered
    # key it adds it to my_instances[]
    my_instances = []
    for x in instances:
      if x.key_name == private_key_name :
        my_instances.append(x)

    if len(my_instances) == 0:
      print("No instances associated with this key. Please ensure it is the")
      print("correct key and that you have created some instances first.")
    else :
      print()
      print("No Name            Status  Time Started")
      print("---------------------------------------")
      for i in range (0, len(my_instances)) :
        print(str(i) + ": " + my_instances[i].tags["Name"] + " " + my_instances[i].state + " " + my_instances[i].launch_time)
      print("\n")
      instance_choice = input("Please enter the number of the instance you wish to manage (x to cancel) >>> ")
      return instance_choice 
  except Exception as e:
    error = str(e)
    print("Something went wrong. Please try again.")
    logger.status_log("view_all_instances method failed. Error: " + error)

# copies a python script from the current directory to the instance. 
def copy_web_script():
  global instance
  if running_check() :
    try :
      print("Copying script...")
      dns = instance.public_dns_name
      
      (status, output) = ssh.copy(dns, private_key_name, "check_webserver.py", "")
      
      if status > 0:
        logger.status_log("Can't connect using ssh. Error message: ")
        logger.status_log(output)
        print("Something isn't quite right. Please try again.")
        return
      
      else :
        (status, output) = ssh.connect(dns, private_key_name, "ls")
        print("Current directory: ")
        print(output)
      
      (status, output) = ssh.connect(dns, private_key_name, "chmod 700 check_webserver.py")
    except Exception as e:
      error = str(e)
      print("Something went wrong. Please try again.")
      logger.status_log("copy_web_script method failed. Error: " + error)

# runs the script copied and asks the user if they would like to start nginx
# if the script returns that it is not already running.
def run_nginx_check():
  global instance
  if running_check() :
    try :
      dns = instance.public_dns_name
      (status, output) = ssh.connect(dns, private_key_name, "sudo python3 check_webserver.py")
      if "command not found" in output:
        print("It doesn't look like you've installed python, please try that first.")
      elif "No such file" in output:
        print("It doesn't look like you've copied the file to the instance, please try that first.")
      else :
        print(output)
        if status > 0 :
          choice = input("Would you like to start nginx? (y/n) ")
          if choice == 'y' :
            (stat, out) = ssh.connect(dns, private_key_name, "sudo service nginx start")
            if "unrecognized service" in out:
              print("It doesn't look like you've installed nginx, please try that first.")
            run_nginx_check()
          else :
            print("Nginx not started.")
    except Exception as e:
      error = str(e)
      print("Something went wrong. Please try again.")
      logger.status_log("run_nginx_check method failed. Error: " + error)

# installs python3.4 on the instance. needed to run the check_webserver script
def install_python():
  global instance
  if running_check() :
    try :
      dns = instance.public_dns_name
      (status, output) = ssh.connect(dns, private_key_name, "sudo yum -y install python34")
      if status == 0:
        print("Python installed successfully!")
      else :
        logger.status_log("Python not installed correctly.")
        try_again = input("Oops, something wen't wrong installing python. Try again? (y/n) ")
        if try_again == 'y':
          install_python()
    except Exception as e:
      error = str(e)
      print("Something went wrong. Please try again.")
      logger.status_log("install_python method failed. Error: " + error)

# allows the user to run their own commands on the instance.
# os.system is used her as opposed to subprocess which is generally used elsewhere
# because of its friendliness with certain commands such as nano etc.
def run_user_command():
  global instance
  if running_check():
    try :
      dns = instance.public_dns_name
      command = None
      print("\nPlease use x to exit the python terminal. ")
      print("Please enter the command you wish to run, don't forget to")
      print("include -y to accept changes if necessary.")
      sudo = input("Would you like to emulate the terminal? (y/n) >>> ")
      while command != 'x':
        command = input(">>> ")
        if command !='x':
          if sudo == 'y':
            cmd = "ssh -t -o StrictHostKeyChecking=no -i " + private_key_name +".pem ec2-user@" + dns + " " + command
            print(os.system(cmd))
          else :
            cmd = "ssh -o StrictHostKeyChecking=no -i " + private_key_name +".pem ec2-user@" + dns + " " + command
            print(os.system(cmd))
    except Exception as e:
      error = str(e)
      print("Something went wrong. Please try again.")
      logger.status_log("run_user_command method failed. Error: " + error)

# opens the index.html page of the nginx server in a new browser tab
def visit_website():
  global instance
  if running_check():
    try :
      dns = instance.public_dns_name
      webbrowser.open("http://" + dns, new=0, autoraise=True)
    except Exception as e:
      error = str(e)
      print("Something went wrong. Please try again.")
      logger.status_log("visit_website method failed. Error: " + error)

# allows the user to view the access log of the server to make sure they are connecting
# and also what ip addresses are connecting.
def view_access_log():
  global instance
  if running_check():
    try :
      dns = instance.public_dns_name
      ssh.connect(dns, private_key_name, "sudo chmod 777 /var/log/nginx")
      cmd = "nano /var/log/nginx/access.log"
      command = "ssh -t -o StrictHostKeyChecking=no -i " + private_key_name + ".pem ec2-user@" + dns + " " + cmd
      print(os.system(command))
    except Exception as e:
      error = str(e)
      print("Something went wrong. Please try again.")
      logger.status_log("view_access_log method failed. Error: " + error)

# allows the user to see what is going wrong if they cannot connect to their
# web server
def view_error_log():
  global instance
  if running_check():
    try :
      dns = instance.public_dns_name
      ssh.connect(dns, private_key_name, "sudo chmod 777 /var/log/nginx")
      cmd = "nano /var/log/nginx/error.log"
      command = "ssh -t -o StrictHostKeyChecking=no -i " + private_key_name +".pem ec2-user@" + dns + " " + cmd
      print(os.system(command))
    except Exception as e:
      error = str(e)
      print("Something went wrong. Please try again.")
      logger.status_log("view_error_log method failed. Error: " + error)

# a helper method which simply checks whether or not their is an instance
# and if their is then whether or not it is running
def running_check():
  global instance
  if instance == None:
    print("No instance selected!")
    logger.status_log("No instance selected.")
  try: 
    instance.update()
    if instance.state == 'running':
      return True
    else :
      print("Instance not running yet, please make sure it is running and then try again.")
      logger.status_log("User tried to access non-running instance.")
      return False
  except Exception as e:
    error = str(e)
    logger.status_log("running_check method failed. Error: " + error)

# The main method is the method which controls the menu and flow of the program.
# All menus are called from the menu.py module in this directory. 
def main():
  menu.start_menu()


  global private_key_name 
  print("Please enter key name, or leave blank for the default (stephencoady)")
  private_key_name = input(" >>> ")
  if private_key_name == "" :
    private_key_name = "stephencoady"

  
  decision = None

  # this while loop controls the "Main Menu"
  while decision != '0':
    menu.main_menu()
    decision = input("Please enter your choice >>> ")
    if decision == '1':
      new_instance()
    if decision == '2':
      print("Gathering information about your instances, please wait.")
      instance_choice = view_all_instances()

  
      global my_instances
      global instance
      if instance_choice != 'x' :
        submenu = None
        try:
          instance = my_instances[int(instance_choice)]
        except Exception as e:
          error = str(e)
          print("Please choose an instance from the list!")
          logger.status_log(error)
          submenu = '0'
        
        # this while loop controls the "Instance Manager" menu
        while submenu != '0':
          menu.instance_manager()
          submenu = input("Please enter your choice >>> ")
          if submenu == '1':
            start_instance()
          if submenu == '2':
            stop_instance()
          if submenu == '3':
            terminate_instance()
          if submenu == '4':
            install_python()
          if submenu == '6':
            run_user_command()
          if submenu == '5':

            # This while loop cntrols the "Nginx Manager" menu
            nginx_choice = None
            while nginx_choice != '0':
              menu.nginx_manager()
              nginx_choice = input("Please enter your choice >>> ")
              if nginx_choice =='1':
                install_nginx()
              if nginx_choice == '2':
                copy_web_script()
              if nginx_choice == '3':
                run_nginx_check()
              if nginx_choice == '4':
                visit_website()
              if nginx_choice == '5':
                view_access_log()
              if nginx_choice == '6':
                view_error_log()

  print("\nExiting! Goodbye!")

if __name__ == '__main__':
  main()
