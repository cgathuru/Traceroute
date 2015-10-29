import platform
import subprocess
import re
import csv
import time
import argparse
import threading
from threading import Thread

__author__ = 'Charles'

traces = list()
lock = threading.Lock()


def main():
    parser = argparse.ArgumentParser(
        description='Runs traceroute command on a given domain name for a given frequency')
    parser.add_argument('--domain', type=str, default='www.google.ca')
    frequency = parser.add_mutually_exclusive_group()
    frequency.add_argument('--hr', action='store_true')
    frequency.add_argument('--day', action='store_true')
    frequency.add_argument('--min', action='store_true')
    parser.add_argument('--rep', type=int, default=1)
    parser.set_defaults(frequency='minute')

    args = parser.parse_args()

    print("Running traceoute.....")
    print("Destination " + args.domain + " Frequency " + args.frequency + " repeating " + str(args.rep))
    domain = args.domain
    command = 'tracert'
    if platform.system() != 'Windows':
        command = 'traceroute'

    print('command is ' + command)

    thread = Thread(target=get_trace_route, args=(command, domain))
    thread.start()
    thread.join()

    print(traces)

    return write_data_to_csv(domain)


def get_trace_route(command, domain):
    content = {}
    output = subprocess.check_output([command, domain])
    decode_out = output.decode("utf-8")
    lines = decode_out.split('\n')
    ip_p = "((([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])[ (\[]?(\.|dot)[ )\]]?){3}([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]))"
    time_pattern = "\d+\sms"
    hops_p = "\d[\s]{2,}"
    hops = 0
    ip_list = list()
    avg_ttl = list()
    for line in lines:
        if line:
            if len([match[0] for match in re.findall(hops_p, line)]) > 0:
                ip = [match[0] for match in re.findall(ip_p, line)]
                if len(ip) > 0 and ip != '*':
                    ip_list.append(ip[0])
                times = re.findall(time_pattern, line)
                if len(times) > 0:
                    avg_ttl.append(times[0].rstrip('ms'))
                hops += 1
    print("Total hops: {}".format(hops))
    print("Ips are:")
    print(ip_list)
    print("Times are:")
    # avg_ttl = list(map(int, avg_ttl))
    content['ips'] = ip_list
    content['times'] = avg_ttl
    content['hops'] = hops
    content['unresponsive'] = hops - len(avg_ttl)
    lock.acquire()
    traces.append(content)
    lock.release()
    return


def write_data_to_csv(domain: str):
    with open(domain + '.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(['Route Number', 'Date', 'Time', 'Destination', 'Route', 'Route TTL', 'Num Hops',
                         'Unresponsive'])
        for route_no, route in enumerate(traces, start=1):
            avg_ttl = route.get('times')
            ip_list = route.get('ips')
            hops = route.get('hops')
            ips = ', '.join(ip_list)

            print(ips)
            writer.writerow([route_no, time.strftime("%x"), time.strftime("%X"), domain, ', '.join(ip_list),
                            ', '.join(avg_ttl), hops, route.get('unresponsive')])
    return


if __name__ == '__main__':
    main()
