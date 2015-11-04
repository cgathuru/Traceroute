import platform
import subprocess
import re
import csv
import time
import argparse
import threading
import concurrent.futures
from  statistics import mean

__author__ = 'Charles'

traces = list()
rtts = list()
lock = threading.Lock()


def main():
    parser = argparse.ArgumentParser(
        description='Runs traceroute command on a given domain name for a given frequency')
    parser.add_argument('--domains', default='www.google.ca', nargs='+', dest='domains')
    frequency = parser.add_mutually_exclusive_group()
    frequency.add_argument('--hr', action='store_true', dest='hour')
    frequency.add_argument('--day', action='store_true', dest="day")
    frequency.add_argument('--min', action='store_true', dest='minute')
    parser.add_argument('--rep', type=int, default=1)
    parser.set_defaults(frequency='minute')

    args = parser.parse_args()

    if args.day:
        seconds = 24*60*60
    elif args.hour:
        seconds = 60*60
    else:
        seconds = 60

    print("Repeating every {} seconds".format(seconds))
    print("Running traceoute.....")
    print("Destinations " + str(args.domains) + " Frequency " + args.frequency + " repeating " + str(args.rep))
    domains = list()
    if type(args.domains) is not list:
        domains.append(str(args.domains))
    else:
        domains = args.domains
    for x in domains:
        print(x)
    file_name = "results_" + time.strftime("%d%m_%H%M", time.localtime())
    command = 'tracert'
    if platform.system() != 'Windows':
        command = 'traceroute'

    print('command is ' + command)

    with concurrent.futures.ThreadPoolExecutor(max_workers=(5*len(domains)*2)) as executor:
        for _ in range(0, args.rep):
            for domain in domains:
                executor.submit(get_trace_route, command, domain)
                executor.submit(get_ping_time, domain)
            time.sleep(seconds)
        executor.shutdown(wait=True)

    print(traces)

    print("Traces length {}".format(len(traces)))
    print("RTTs length {}".format(len(rtts)))

    return write_data_to_csv(file_name)


def get_ping_time(domain):
    num_pkts = 3
    command = 'ping -n {} {}'.format(num_pkts, domain)
    if platform.system() != 'Windows':
        command = 'ping -c {} {}'.format(num_pkts, domain)
    output = subprocess.check_output(command)
    decode_out = output.decode("utf-8")
    lines = decode_out.split('\n')
    ttl = -1
    times = []
    for line in lines:
        matches = re.match('.*time=([0-9]+)ms.*', line)
        if matches:
            times.append(matches.group(1))
    if times:
        ttl = mean(list(map(int, times)))
    ttl = float(format(ttl, '.2f'))
    lock.acquire()
    rtts.append(ttl)
    lock.release()
    print("Average ttl:  {}".format(ttl))


def get_trace_route(command, domain):
    content = dict()
    content['domain'] = domain
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
    content['date'] = time.strftime("%x")
    content['time'] = time.strftime("%X")
    lock.acquire()
    traces.append(content)
    lock.release()
    return


def write_data_to_csv(file_name: str):
    with open(file_name + '.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(['Route Number', 'Date', 'Time', 'Destination', 'Route', 'Route TTL', 'Num Hops',
                         'Unresponsive', 'Average RTT'])
        for route_no, route in enumerate(traces, start=1):
            route_ttls = route.get('times')
            ip_list = route.get('ips')
            hops = route.get('hops')
            domain = route.get('domain')
            avg_rtt = rtts[route_no-1]

            writer.writerow([route_no, route.get('date'), route.get('time'), domain, ', '.join(ip_list),
                            ', '.join(route_ttls), hops, route.get('unresponsive'), avg_rtt])
    return


if __name__ == '__main__':
    main()
