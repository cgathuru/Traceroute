import graphviz as gv
import csv
import functools
import statistics
from datetime import datetime


__author__ = 'Charles'


def main():

    # We need to be able to compare different times
    start_date_1 = datetime.strptime('11/5/2015 8:07:27', "%m/%d/%Y %H:%M:%S")
    end_date_1 = datetime.strptime('11/5/2015 8:30:27', "%m/%d/%Y %H:%M:%S")
    start_date_2 = datetime.strptime('11/5/2015 8:30:27', "%m/%d/%Y %H:%M:%S")
    end_date_2 = datetime.strptime('11/5/2015 9:05:27', "%m/%d/%Y %H:%M:%S")
    digraph = functools.partial(gv.Digraph, format='svg')
    # WE need to build a list edge sets
    time_set1 = {}
    time_set2 = {}
    domain_set = {}
    with open('results_0511_0807.csv', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        next(reader, None)
        for row in reader:
            domain = row[4]
            date = row[1]
            time = row[2]
            time_string = date + ' ' + time
            time_obj = datetime.strptime(time_string, "%m/%d/%y %H:%M:%S")
            if (time_obj < start_date_1) and (time_obj < start_date_2):
                continue
            if (time_obj > end_date_1) and (time_obj > end_date_2):
                continue
            ips = row[5].split(', ')
            rtts = row[6].split(', ')
            edge_sets = list()
            for index, ip in enumerate(ips, start=0):
                if index != 0:
                    data = [ips[index - 1], ips[index], list(), 0]
                    if ip == '*':
                        data[3] += 1
                    else:
                        data[2].append(str(rtts[index]))

                    edge_sets.append(data)
                    if (time_obj > start_date_1) and (time_obj < end_date_1):
                        if not time_set1.__contains__(domain):
                            time_set1[domain] = edge_sets
                    elif (time_obj > start_date_2) and (time_obj < end_date_2):
                        if not time_set2.__contains__(domain):
                            time_set2[domain] = edge_sets

            else:
                # We need to modify existing
                for set_temp in edge_sets:
                    if (time_obj > start_date_1) and (time_obj < end_date_1):
                        for index in range(len(time_set1[domain])):
                            edge_set = time_set1[domain][index]
                            if edge_set[0] == set_temp[0]:
                                if edge_set[1] == set_temp[1]:
                                    edge_set[2] += set_temp[2]
                                    edge_set[3] += set_temp[3]
                                    break
                        else:
                            # Set was not found
                            time_set1[domain].append(set_temp)
                    elif (time_obj > start_date_2) and (time_obj < end_date_2):
                        for index in range(len(time_set2[domain])):
                            edge_set = time_set2[domain][index]
                            if edge_set[0] == set_temp[0]:
                                if edge_set[1] == set_temp[1]:
                                    edge_set[2] += set_temp[2]
                                    edge_set[3] += set_temp[3]
                                    break
                        else:
                            # Set was not found
                            time_set2[domain].append(set_temp)

    for domain, data in time_set1.items():
        print(domain)
        print(data)

    for domain, data in time_set2.items():
        print(domain)
        print(data)

    # print(graphs[0].source)
    # for num, graph in enumerate(graphs):
       # render_graph(graph, num)
    build_graphs(domain_set=time_set1, filename_suffix='set_1')
    build_graphs(domain_set=time_set2, filename_suffix='set_2')


def build_graphs(domain_set, filename_suffix):
    for domain in domain_set:
        g1 = gv.Digraph(format='svg',
                        graph_attr={'label': '{}'.format(domain), 'labelloc': 't', 'fontsize': '30'})
        for index, edge_data in enumerate(domain_set[domain], start=0):
            if index == 0:
                g1.node(edge_data[index])
            g1.node(edge_data[1])
            label = make_label(edge_data)
            g1.edge(edge_data[0], edge_data[1], label=label+"_"+filename_suffix)
        else:
            render_graph(g1, domain, filename_suffix)


def make_label(edge_data):
    label = ''
    rtts = list(map(float, edge_data[2]))
    unresponsive = edge_data[3]
    if rtts:
        rtt_avg = float(format(statistics.mean(rtts), '.2f'))
        if len(rtts) > 1:
            rtt_var = float(format(statistics.variance(rtts, rtt_avg), '.2f'))
            rtt_sd = float(format(statistics.stdev(rtts, rtt_avg), '.2f'))
        else:
            rtt_var = rtt_sd = -1
    else:
        rtt_avg = rtt_var = rtt_sd = -1

    label = label + 'Average RTT: {}, Var: {}\n SD: {}, Times Unresponsive: {}'\
        .format(rtt_avg, rtt_var, rtt_sd, unresponsive)

    print(label)

    return label


def add_nodes(graph, nodes):
    for n in nodes:
        if isinstance(n, tuple):
            graph.node(n[0], **n[1])
        else:
            graph.node(n)
    return graph


def add_edges(graph, edges):
    for e in edges:
        if isinstance(e[0], tuple):
            graph.edge(*e[0], **e[1])
        else:
            graph.edge(*e)
    return graph


def render_graph(graph, num, filename_suffix):
    filename = graph.render(filename='img/g{}_{}'.format(num, filename_suffix))
    print(filename)


if __name__ == '__main__':
    main()
