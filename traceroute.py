import platform
import sys
import subprocess
import re
import csv
import time
#import statistics

__author__ = 'Charles'


def main():
    domain = sys.argv[1] if len(sys.argv) > 1 else "www.google.ca"
    frequency = sys.argv[2] if len(sys.argv) > 2 else 1
    frequency = int(frequency)
    frequency_unit = sys.argv[3] if len(sys.argv) > 3 else "s"
    duration = sys.argv[4] if len(sys.argv) > 4 else 1
    duration = int(duration)
    duration_unit = sys.argv[5] if len(sys.argv) > 5 else "m"
    command = 'tracert'
    if platform.system() != 'Windows':
        command = 'traceroute'

    print('command is ' + command)

    #get the time 
    time_to_sleep = 0 
    if frequency_unit == "s":
        time_to_sleep = frequency 
    elif frequency_unit == "m":
        time_to_sleep = frequency * 60
    elif frequency_unit == "h":
        time_to_sleep = frequency * 3600
    elif frequency_unit == "d": 
        time_to_sleep = frequency * 3600 * 24

    iteration_count = 0 
    if duration_unit == "s":
        if frequency_unit == "s":
            iteration_count = duration / frequency
        else:
            print("Bad unit combination\n")
            return 1
    elif duration_unit == "m":
        if frequency_unit == "s":
            iteration_count = 60 * duration / frequency
        elif frequency_unit == "m":
            iteration_count = duration / frequency
        else:
            print("Bad unit combination \n")
            return 1
    elif duration_unit == "h":
        if frequency_unit == "s":
            iteration_count = 3600 * duration / frequency
        elif frequency_unit == "m":
            iteration_count = 60 * duration / frequency
        elif frequency_unit == "h":
            iteration_count = duration/frequency
        else:
            print("Bad unit combination \n")
            return 1
    elif duration_unit == "d":
        if frequency_unit == "s":
            iteration_count = 24*3600 * duration / frequency
        elif frequency_unit == "m":
            iteration_count = 24* 60 * duration / frequency
        elif frequency_unit == "h":
            iteration_count = 24* duration/frequency
        elif frequency_unit == "d":
            iteration_count = duration/frequency
        else:
            print("Bad unit combination \n")
            return 1
    else: 
        print("bad input \n")
        return 1

    print ("Traceroute will run every " + str(time_to_sleep) +" seconds " + str(iteration_count) + " times \n")

    for x in range (0, iteration_count):
        get_traceroute_output(command, domain)
        time.sleep(time_to_sleep)




def get_traceroute_output(command, host):

	with open("results.txt", "a") as output:
		print ("Tracing", host)

		trace = subprocess.Popen([command, "-w", "100", host], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		while True:
		    hop = trace.stdout.readline()

		    if not hop: break

		    print '-->', hop.strip()
		    output.write(hop)

		# When you pipe stdout, the doc recommends that you use .communicate()
		# instead of wait()
		# see: http://docs.python.org/2/library/subprocess.html#subprocess.Popen.wait
		trace.communicate()


if __name__ == '__main__':
    main()
