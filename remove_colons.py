import sys
import csv
import re

__author__ = 'Charles'


def main():
    filename = sys.argv[1]
    outfile = filename[:-4] + "_amended.csv"
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        with open(outfile, mode='w', newline='') as csv_file_out:
            fieldnames = csv_reader.fieldnames
            filtered_routes = map(remove_ip_hops, csv_reader)
            print(fieldnames)
            writer = csv.DictWriter(csv_file_out, fieldnames)
            writer.writeheader()
            writer.writerows(filtered_routes)


def remove_ip_hops(traceroute: dict):
    ip_list = traceroute.get('Route').split(',')
    filtered_list = [re.sub(r':\d+', '', ip) for ip in ip_list]
    route = {'Route': ','.join(filtered_list)}
    traceroute.update(route)
    return traceroute


if __name__ == '__main__':
    main()
