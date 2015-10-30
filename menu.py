# A helper module to simply print menus to the user.
# This python module keeps the main code clean and readable.

def start_menu():
  print('\n################################################')
  print('#                  AWS Manager                 #')
  print('################################################')
  print('# Welcome to AWS Manager. A program to help    #')
  print('# you manage your AWS instances.               #')
  print('# Please enter the name of your .pem key below,#')
  print('# without the extension and ensure it is in    #')
  print('# the current directory.                       #')
  print('#                                              #')
  print('################################################\n')

def main_menu():
  print('\n|==============================================|')
  print('|                  Main Menu                   |')
  print('|==============================================|')
  print('| 1) Create new instance                       |')
  print('| 2) Manage your current instances             |')
  print('| 0) Exit                                      |')
  print('|______________________________________________|\n')


def instance_manager():
  print('\n|==============================================|')
  print('|              Instance Manager                |')
  print('|==============================================|')
  print('| 1) Start instance                            |')
  print('| 2) Stop instance                             |')
  print('| 3) Terminate instance                        |')
  print('| 4) Install python                            |')
  print('| 5) Nginx Manager                             |')
  print('| 6) Enter your own command on the instance    |')
  print('| 0) Return                                    |')
  print('|______________________________________________|\n')

def nginx_manager():
  print('\n|==============================================|')
  print('|                Nginx Manager                 |')
  print('|==============================================|')
  print('| 1) Install nginx                             |')
  print('| 2) Copy check_webserver script to instance   |')
  print('| 3) Run nginx checking script                 |')
  print('| 4) View html of nginx server landing page    |')
  print('| 5) View nginx access logs                    |')
  print('| 6) View nginx error logs                     |')
  print('| 0) Return                                    |')
  print('|______________________________________________|\n')