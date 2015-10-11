import platform
import sys
import subprocess
import re

__author__ = 'Charles'


def main():
    domain = sys.argv[1] if len(sys.argv) > 1 else "www.google.ca"
    frequency = sys.argv[2] if len(sys.argv) > 2 else 1
    multiplicity = sys.argv[3] if len(sys.argv) > 3 else 1
    command = 'tracert'
    if platform.system() != 'Windows':
        command = 'traceroute'

    print('command is ' + command)
    output = subprocess.check_output([command, domain])
    decode_out = output.decode("utf-8")
    lines = decode_out.split('\n')
    # p = re.compile('(\d)|(\d+\sms)|([A-za-z\.]+)|(\*)|(\[[0-9\\.]+\])')
    ip_p = "((([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])[ (\[]?(\.|dot)[ )\]]?){3}([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]))"
    time_pattern = "\d+\sms"
    hops_p = "\d[\s]{2,}"
    i = 0
    hops = 0
    for line in lines:
        if line:
            print("Line {}".format(i) + " " + line)
            ip = [match[0] for match in re.findall(ip_p, line)]
            times = [match[0] for match in re.findall(time_pattern, line)]
            hops = hops + 1 if len([match[0] for match in re.findall(hops_p, line)]) > 0 else hops
            print('Found {} ip matches'.format(len(ip)))
            print('Found {} time matches'.format(len(times)))
        i += 1

    print("Total hops: {}".format(hops))


if __name__ == '__main__':
    main()
