#!/usr/bin/python

import time, datetime, csv
from mininet.node import Controller, OVSKernelSwitch, Host
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference
from matplotlib import pyplot as plt
from mininet.term import runX11


def createfile():
    datetimenow = str(datetime.datetime.now()).split(' ')
    datenow = datetimenow[0]
    mode = datetimenow[1][:8].split(':')
    s1 = int(mode[0])
    s2 = int(mode[1])
    s3 = int(mode[2])
    s1 = s1 * 10000 + s2 * 100 + s3
    timenow = s1
    mode = datenow.split('-')
    s1 = int(mode[0])
    s2 = int(mode[1])
    s3 = int(mode[2])
    s1 = s1 * 10000 + s2 * 100 + s3
    datenow = s1
    filename = 'output' + str(timenow) + '_' + str(datenow)
    filename += '.csv'

    print('Name of File created :', filename)
    return filename


def plot_graph(filename):
    aps, throughput, distance, times, handovers = ([] for i in range(5))
    flag = 0
    for i in range(7):
        ap, thpt, dist, time, handover = ([] for i in range(5))
        with open(filename[i], 'r') as csvfile:
            rows = csv.reader(csvfile)
            for row in rows:
                ap.append(row[1])
                thpt.append(row[2])
                dist.append(row[3])
                time.append(row[4])
                handover.append(row[-1])
        aps.append(ap[1:])
        thpt = [float(item) for item in thpt[1:]]
        dist = [float(item) for item in dist[1:]]
        time = [float(item) for item in time[1:]]
        handover = handover[1:]
        throughput.append(thpt)
        distance.append(dist)
        times.append(time)
        handovers.append(handover)
        plt.plot(times[i], throughput[i], label='sta%s' % (i + 1))
        plt.ylabel('Throughput(Mbps)')
        plt.xlabel('time(sec)')
        plt.title('Throughput vs time')
        plt.legend(loc='best')
        for j, ho in enumerate(handovers[i]):
            if ho == '1':
                if j == 0:
                    continue
                if flag == 0:
                    plt.plot(times[i][j], throughput[i][j], 'ro', label='Handover')
                    flag = 1
                plt.plot(times[i][j], throughput[i][j], 'ro')

    plt.show()


def topology():
    net = Mininet_wifi(topo=None,
                       build=False,
                       link=wmediumd,
                       wmediumd_mode=interference,
                       ipBase='10.0.0.0/8')

    info('*** Adding controller\n')
    c0 = net.addController(name='c0',
                           controller=Controller,
                           protocol='tcp',
                           port=6633)

    info('*** Add switches/APs\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    ap1 = net.addAccessPoint('ap1', cls=OVSKernelAP, ssid='ap-ssid',
                             channel='1', mode='n', failMode='standalone', position='20.0,80.0,0.0', range=42)
    ap2 = net.addAccessPoint('ap2', cls=OVSKernelAP, ssid='ap-ssid',
                             channel='6', mode='n', failMode='standalone', position='80.0,80.0,0.0', range=42)
    ap3 = net.addAccessPoint('ap3', cls=OVSKernelAP, ssid='ap-ssid',
                             channel='1', mode='n', failMode='standalone', position='80.0,20.0,0.0', range=42)
    ap4 = net.addAccessPoint('ap4', cls=OVSKernelAP, ssid='ap-ssid',
                             channel='6', mode='n', failMode='standalone', position='20.0,20.0,0.0', range=42)

    info('*** Add hosts/stations\n')
    nodes = {}
    for i in range(7):
        nodes['sta%s' % (i + 1)] = net.addStation('sta%s' % (i + 1),
                                                  ip='10.0.0.%s/8' % (i + 2), min_x=25, max_x=75, min_y=25, max_y=75,
                                                  min_v=1, max_v=1.5)
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model='logNormalShadowingPropagationLossModel', exp=4.5, variance=1)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info('*** Add links\n')
    net.addLink(h1, s1)
    net.addLink(ap1, s1)
    net.addLink(ap2, s1)
    net.addLink(ap3, s1)
    net.addLink(ap4, s1)

    net.plotGraph(min_x=-40, max_x=150, min_y=-40, max_y=150)
    net.setMobilityModel(time=0, model='RandomWalk')
    net.startMobility(time=0, AC='ssf')
    info('*** Starting network\n')
    net.build()
    info('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info('*** Starting switches/APs\n')
    net.get('s1').start([c0])
    net.get('ap1').start([])
    net.get('ap2').start([])
    net.get('ap3').start([])
    net.get('ap4').start([])

    info('*** Post configure nodes\n')
    time.sleep(5)
    val = input('Data Collection: ')
    if val == 'yes':
        filename = []
        info('*** Creating files for data storage\n')
        for i in range(7):
            file = createfile()
            file -= '.csv'
            file += 'sta %s' % (i + 1) + '.csv'
            header_name = ["staName", "APName", "thpt", "dist", "time", "handover"]
            with open(file, 'w+') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(header_name)

            filename.append(file)
        info('Starting iperf server\n')
        h1.cmd('iperf -s -p 5566 -i 1 -t 600 &')

        info('collecting data\n')
        startime = time.time()
        currenttime = time.time()
        difftime = currenttime - startime
        connected_ap = [1, 2, 3, 0, 1, 2, 0]

        while difftime < 500:
            for i in range(7):
                name = 'sta%s' % (i + 1)
                associated_to = nodes[name].cmd('iw dev sta%s-wlan0 link' % (i + 1))
                associated_to = str(associated_to).splitlines()
                status = associated_to[0].split(' ')[0]
                if status == 'Not':
                    print('sta%s is not connected' % (i + 1))
                    continue

                clientdata = nodes[name].cmd('iperf -c 10.0.0.1 -p 5566 -i 1 -t 1')
                print(clientdata)
                thpt = clientdata.splitlines()[-1].split(' ')[-2]

                if thpt == 'to' or thpt == 'in':
                    print('Connection to iperf server lost')
                    continue
                if clientdata.splitlines()[-1].split(' ')[-1] == 'Kbits/sec':
                    thpt = str(float(thpt) / 1000)
                dist1 = nodes[name].get_distance_to(ap1)
                dist2 = nodes[name].get_distance_to(ap2)
                dist3 = nodes[name].get_distance_to(ap3)
                dist4 = nodes[name].get_distance_to(ap4)
                distance = [dist1, dist2, dist3, dist4]
                short_index = distance.index(min(distance))
                handover = 0
                distance_ap = distance[connected_ap[i]]
                if (connected_ap[i] != short_index) and (distance_ap > 42):
                    connected_ap[i] = short_index
                    distance_ap = distance[connected_ap[i]]
                    print('Handover happened at sta%s' % (i + 1))
                    handover = 1

                ap_name = 'ap%s' % (connected_ap[i] + 1)
                currenttime = time.time()
                difftime = currenttime - startime
                difftimeval = "{:.2f}".format(difftime)
                data_list = [name, ap_name, thpt, distance_ap, difftimeval, handover]
                print(data_list)
                with open(filename[i], 'a') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(data_list)
        # TODO
        # info('*** Plotting Graphs\n')
        # plot_graph(filename)
    else:
        time.sleep(2)
        ap_mac = [ap1.cmd('ifconfig ap1-wlan1 | grep ether').splitlines()[-1].split()[1].upper(),
                  ap2.cmd('ifconfig ap2-wlan1 | grep ether').splitlines()[-1].split()[1].upper(),
                  ap3.cmd('ifconfig ap3-wlan1 | grep ether').splitlines()[-1].split()[1].upper(),
                  ap4.cmd('ifconfig ap4-wlan1 | grep ether').splitlines()[-1].split()[1].upper()]
        time.sleep(3)
        runX11(h1, 'python server.py')
        print('ap_mac', ap_mac)
        nodes['sta1'].cmd('./client.sh &')
        time.sleep(1)
        try:
            mcs = nodes['sta1'].cmd('iw dev sta1-wlan0 station dump | grep MCS').splitlines()[-1].split(' ')[-1]
            print('MCS: ', mcs)
        except IndexError:
            print('MCS not found')
        print('SINR: ', nodes['sta1'].cmd('iwconfig | grep Link').splitlines()[-1].split()[1].split('=')[1])
        print('sta1 is connected to', ap_mac.index(nodes['sta1'].cmd('iwconfig | '
                                                                     'grep Access').splitlines()[-1].split()[-1]) + 1)
        time.sleep(4)
        info('*** Starting iperf server and client')
        filename = createfile()
        header = ["thpt", "ap_name", "nosta", "mcs", "sinrval", "time"]
        with open(filename, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(header)

        h1.cmd('iperf -s -p 5566 -i 1 -t 600 &')
        startime = time.time()
        currenttime = time.time()
        difftime = currenttime - startime
        while difftime < 500:
            associated_to = nodes['sta1'].cmd('iw dev sta1-wlan0 link')
            associated_to = str(associated_to).splitlines()
            status = associated_to[0].split(' ')[0]
            if status == 'Not':
                print('sta1 is not connected')
                continue

            clientdata = nodes['sta1'].cmd('iperf -c 10.0.0.1 -p 5566 -i 1 -t 1')
            print(clientdata)
            thpt = clientdata.splitlines()[-1].split(' ')[-2]

            if thpt == 'to' or thpt == 'in':
                print('Connection to iperf server lost')
                continue
            if clientdata.splitlines()[-1].split(' ')[-1] == 'Kbits/sec':
                thpt = str(float(thpt) / 1000)
            mcs = nodes['sta1'].cmd('iw dev sta1-wlan0 station dump | grep MCS').splitlines()[-1].split(' ')[-1]
            currenttime = time.time()
            difftime = currenttime - startime
            difftimeval = "{:.2f}".format(difftime)
            mac_ap = nodes['sta1'].cmd('iwconfig | grep Access').splitlines()[-1].split()[-1]
            if mac_ap == 'dBm':
                continue
            ap_name = ap_mac.index(mac_ap) + 1
            nosta = 1
            sinrval = nodes['sta1'].cmd('iwconfig | grep Link').splitlines()[-1].split()[1].split('=')[1]
            for i in range(1, 7):
                name = 'sta%s' % (i+1)
                mac_ap = nodes[name].cmd('iwconfig | grep Access').splitlines()[-1].split()[-1]
                if mac_ap == 'dBm':
                    continue
                if ap_mac.index(mac_ap) == ap_name:
                    nosta += 1
            data_list = [thpt, ap_name, nosta, mcs, sinrval, difftimeval]
            print(data_list)
            with open(filename, 'a') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(data_list)
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
