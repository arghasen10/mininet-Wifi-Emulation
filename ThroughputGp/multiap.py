#!/usr/bin/python

import time, datetime, csv
from mininet.node import OVSKernelSwitch, Host
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
        ap, thpt, dist, time1, handover = ([] for i in range(5))
        with open(filename[i], 'r') as csvfile:
            rows = csv.reader(csvfile)
            for row in rows:
                ap.append(row[1])
                thpt.append(row[2])
                dist.append(row[3])
                time1.append(row[4])
                handover.append(row[-1])
        aps.append(ap[1:])
        thpt = [float(item) for item in thpt[1:]]
        dist = [float(item) for item in dist[1:]]
        time1 = [float(item) for item in time1[1:]]
        handover = handover[1:]
        throughput.append(thpt)
        distance.append(dist)
        times.append(time1)
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

    info('*** Add switches/APs\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')
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
        nodes['sta%s' % (i + 1)] = net.addStation('sta%s' % (i + 1), mac='00:00:00:00:00:0%s' % (i+2),
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

    info('*** Starting switches/APs\n')
    net.get('s1').start([])
    net.get('ap1').start([])
    net.get('ap2').start([])
    net.get('ap3').start([])
    net.get('ap4').start([])

    info('*** Post configure nodes\n')
    time.sleep(5)
    sta_MAC = []
    for i in range(7):
        sta_MAC.append(nodes['sta%s' % (i + 1)].params['mac'])
    print(sta_MAC)
    val = input('Data Collection: ')

    if val == 'yes':
        info('*** Creating file for data storage\n')
        file = createfile()
        header_name = ["staName", "APName", "thpt", "dist", "time", "handover"]
        with open(file, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(header_name)

        info('Starting iperf server\n')
        h1.cmd('iperf -s -p 5566 -i 1 -t 600 &')

        info('collecting data\n')
        startime = time.time()
        currenttime = time.time()
        difftime = currenttime - startime
        prev_connected_ap = 1
        new_connected_ap = 1
        distance_ap = 0
        while difftime < 500:
            name = 'sta1'
            associated_to = nodes[name].cmd('iw dev sta1-wlan0 link')
            associated_to = str(associated_to).splitlines()
            status = associated_to[0].split()[0]
            if status == 'Not':
                print('sta1 is not connected')
                continue
            clientdata = nodes['sta1'].cmd('iperf -c 10.0.0.1 -p 5566 -i 1 -t 10 | ts | grep sec &').splitlines()
            for res in clientdata:
                print(res.split()[-2], res.split()[-1])
            thpt = clientdata[-1].split()[-2]

            if thpt == 'to' or thpt == 'in':
                print('Connection to iperf server lost')
                continue
            if clientdata.splitlines()[-1].split()[-1] == 'Kbits/sec':
                thpt = float(thpt) / 1000
            handover = 0
            res = ap1.cmd('hostapd_cli -i ap1-wlan1 all_sta | grep ..:').splitlines()
            if nodes['sta1'].params['mac'] in res:
                new_connected_ap = 1
                distance_ap = nodes['sta1'].get_distance_to(ap1)
            res = ap2.cmd('hostapd_cli -i ap2-wlan1 all_sta | grep ..:').splitlines()
            if nodes['sta1'].params['mac'] in res:
                new_connected_ap = 2
                distance_ap = nodes['sta1'].get_distance_to(ap2)
            res = ap3.cmd('hostapd_cli -i ap3-wlan1 all_sta | grep ..:').splitlines()
            if nodes['sta1'].params['mac'] in res:
                new_connected_ap = 3
                distance_ap = nodes['sta1'].get_distance_to(ap3)
            res = ap4.cmd('hostapd_cli -i ap4-wlan1 all_sta | grep ..:').splitlines()
            if nodes['sta1'].params['mac'] in res:
                new_connected_ap = 4
                distance_ap = nodes['sta1'].get_distance_to(ap4)
            if prev_connected_ap != new_connected_ap:
                handover = 1
                prev_connected_ap = new_connected_ap
                print('Handover happened from ap%s to ap%s' % (prev_connected_ap, new_connected_ap))

            ap_name = 'ap%s' % new_connected_ap
            currenttime = time.time()
            difftime = currenttime - startime
            difftimeval = "{:.2f}".format(difftime)
            data_list = [name, ap_name, thpt, distance_ap, difftimeval, handover]
            print(data_list)
            with open(file, 'a') as csv_file:
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
        # time.sleep(3)
        # runX11(h1, 'python server.py')
        # print('ap_mac', ap_mac)
        # nodes['sta1'].cmd('./client.sh &')
        # time.sleep(1)
        # try:
        #     mcs = nodes['sta1'].cmd('iw dev sta1-wlan0 station dump | grep MCS').splitlines()[-1].split(' ')[-1]
        #     print('MCS: ', mcs)
        # except IndexError:
        #     print('MCS not found')
        # print('SINR: ', nodes['sta1'].cmd('iwconfig | grep Link').splitlines()[-1].split()[1].split('=')[1])
        # print('sta1 is connected to', ap_mac.index(nodes['sta1'].cmd('iwconfig | '
        #                                                              'grep Access').splitlines()[-1].split()[-1]) + 1)
        # time.sleep(4)
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
            associated_to = nodes['sta7'].cmd('iw dev sta7-wlan0 link')
            associated_to = str(associated_to).splitlines()
            status = associated_to[0].split(' ')[0]
            if status == 'Not':
                print('sta7 is not connected')
                continue

            clientdata = nodes['sta7'].cmd('iperf -c 10.0.0.1 -p 5566 -i 1 -t 1')
            print(clientdata)
            thpt = clientdata.splitlines()[-1].split()[-2]

            if thpt == 'to' or thpt == 'in':
                print('Connection to iperf server lost')
                continue
            if clientdata.splitlines()[-1].split()[-1] == 'Kbits/sec':
                thpt = str(float(thpt) / 1000)
            mcs = nodes['sta7'].cmd('iw dev sta7-wlan0 station dump | grep MCS').splitlines()[-1].split()[-1]
            currenttime = time.time()
            difftime = currenttime - startime
            difftimeval = "{:.2f}".format(difftime)
            mac_ap = nodes['sta7'].cmd('iwconfig | grep Access').splitlines()[-1].split()[-1]
            if mac_ap == 'dBm':
                print('No access point details found', nodes['sta7'].cmd('iwconfig | grep Access'))
                continue
            ap_name = ap_mac.index(mac_ap) + 1
            nosta = 1
            sinrval = nodes['sta7'].cmd('iwconfig | grep Link').splitlines()[-1].split()[1].split('=')[1]
            for i in range(7):
                if i == 6:
                    continue
                name = 'sta%s' % (i+1)
                mac_ap = nodes[name].cmd('iwconfig | grep Access').splitlines()[-1].split()[-1]
                if mac_ap == 'dBm':
                    print('No access point details found for %s' % name, nodes[name].cmd('iwconfig | grep Access'))
                    continue
                if (ap_mac.index(mac_ap)+1) == ap_name:
                    print('%s is connected to %s' % (name, ap_name))
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
