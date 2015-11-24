import platform
import subprocess
import re
import csv
import time
import argparse
import threading
import concurrent.futures
from statistics import mean

__author__ = 'Charles'

traces = list()
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

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(domains)*3) as executor:
        for _ in range(0, args.rep):
            for domain in domains:
                future_trace = executor.submit(get_trace_route, command, domain, executor)
                traces.append(future_trace.result())
            time.sleep(seconds)
        executor.shutdown(wait=True)

    return write_data_to_csv(file_name)


def get_ping_time(domain):
    num_pkts = 3
    command = 'ping -n {} {}'.format(num_pkts, domain)
    if platform.system() != 'Windows':
        command = 'ping -c {} {}'.format(num_pkts, domain)
    try:
        output = subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError:
        print("ping error. Destination {} may be unreachable".format(domain))
        return -1
    decode_out = output.decode("utf-8")
    lines = decode_out.split('\n')
    ttl = -1
    times = []
    for line in lines:
        matches = re.search('time=([0-9.]+)\s?ms', line)
        if matches:
            times.append(matches.group(1))
    if times:
        ttl = mean(list(map(float, times)))
    if ttl == -1:
        with open("error.txt", 'a') as file:
            file.writelines(str(output))
    ttl = float(format(ttl, '.2f'))
    # lock.acquire()
    # rtts.append(ttl)
    # lock.release()
    print("Average rtt:  {}".format(ttl))
    return ttl


def get_trace_route(command, domain, excecutor):
    content = dict()
    content['domain'] = domain
    content['date'] = time.strftime("%x")
    content['time'] = time.strftime("%X")
    future = excecutor.submit(get_ping_time, domain)
    content['avg_rtt'] = future.result()
    output = subprocess.check_output([command, domain])
    decode_out = output.decode("utf-8")
    lines = decode_out.split('\n')
    ip_p = "((([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])[ (\[]?(\.|dot)[ )\]]?){3}([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]))"
    time_pattern = "\d+\sms"
    hops_p = "\d[\s]{2,}"
    no_resp_p = "\*"
    hops = 0
    ip_list = list()
    avg_ttl = list()
    hops_counter = 1
    unresponsive = 0
    for line in lines:
        if line:
            if len([match[0] for match in re.findall(hops_p, line)]) > 0:
                ip = [match[0] for match in re.findall(ip_p, line)]
                if len(ip) > 0 and ip != '*':
                    ip_list.append(ip[0]+":{}".format(hops + 1))
                else:
                    ip_list.append('*:{}'.format(hops + 1))
                    print("Added fake ip")
                    unresponsive += 1
                times = re.findall(time_pattern, line)
                if len(times) > 0:
                    avg_ttl.append(times[0].rstrip('ms'))
                    hops_counter += len(times)
                unresp = re.findall(no_resp_p, line)

                if len(unresp) > 0:
                    print("Found unresponsive node")
                    hops_counter += len(unresp)
                if hops_counter >= 3:  # just in case the ip also return *
                    hops_counter = 0
                    hops += 1

    content['ips'] = ip_list
    content['times'] = avg_ttl
    content['hops'] = hops
    content['unresponsive'] = unresponsive
    content['end_time'] = time.strftime("%X")

    # lock.acquire()
    # traces.append(content)
    # lock.release()
    print("Returning content")
    return content


def write_data_to_csv(file_name: str):
    with open(file_name + '.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(['Route Number', 'Date', 'Time', 'End Time', 'Destination', 'Route', 'Route RTT', 'Num Hops',
                         'Unresponsive', 'Average RTT'])
        for route_no, route in enumerate(traces, start=1):
            route_ttls = route.get('times')
            ip_list = route.get('ips')
            hops = route.get('hops')
            domain = route.get('domain')
            avg_rtt = route.get('avg_rtt')

            writer.writerow([route_no, route.get('date'), route.get('time'), route.get('end_time'), domain,
                             ', '.join(ip_list), ', '.join(route_ttls), hops, route.get('unresponsive'), avg_rtt])
    return


def test():
    line = "12 * * *      unresponsive"
    no_resp_p = "\*"
    no_resp = re.findall(no_resp_p, line)
    if no_resp:
        print("Found {}".format(len(no_resp)))


if __name__ == '__main__':
    main()
    #test()

