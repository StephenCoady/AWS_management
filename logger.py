# This module will simply print an activity monitor for the developer
# Stephen Coady
# 20064122

from time import strftime

def status_log(message):
  date_time = strftime("| %d/%m/%Y | %H:%M:%S | ")
  with open("output.txt", "a") as text_file:
    print(str(date_time) + " " + message, file=text_file)
