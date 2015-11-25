import sys
import csv
import re

__author__ = 'Charles'


routes = {}


def main():
    filename = sys.argv[1]
    outfile = filename[:-4] + "_unresponsive.txt"
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        fieldnames = csv_reader.fieldnames
        for traceroute in csv_reader:
            calculate_unresponsive(traceroute)
        print("Maps")
        print(fieldnames)
        with open(outfile, mode='w') as writer:
            for destination in routes:
                writer.write(destination + ": " + str(routes[destination]) + " , Percentage Unresponsive {:.0%}\n"
                             .format(float(routes[destination][0])/float(routes[destination][1])))


def calculate_unresponsive(traceroute: dict):
    destination = traceroute.get('Destination')
    unresponsive = int(traceroute.get('Unresponsive'))
    num_hops = int(traceroute.get('Num Hops'))

    ip_list = re.search('\*:1', traceroute.get('Route'))
    if ip_list:
        unresponsive -= 1
    if not routes.__contains__(destination):
        routes[destination] = [0, 0]
    routes[destination][0] += unresponsive
    routes[destination][1] += num_hops
    return routes
    pass


if __name__ == '__main__':
    main()
