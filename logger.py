#!/usr/bin/python3

# This class will simply allow the user to see one message
# while also printing an activity monitor for the developer
# Stephen Coady
# 20064122

from time import strftime

def error_log(error):
  date_time = strftime("| %d/%m/%Y | %H:%M:%S | ")
  
  with open("output.txt", "a") as text_file:
    print(str(date_time) + " " + error, file=text_file)
