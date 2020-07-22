#!/usr/bin/python

from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
import time
import csv

throughput_list = []
distance_list = []


def topology():
    net = Mininet_wifi()

    info('**Creating Nodes**\n')
    h1 = net.addHost('h1', mac='00:00:00:00:00:01', ip='10.0.0.1/8')
    sta1 = net.addStation('sta1', mac='00:00:00:00:00:02', ip='10.0.0.2/8', range=30)
    ap1 = net.addAccessPoint('ap1', ssid='api-ssid', mode='n', channel='1', position='80,40,0', range=30)
    c1 = net.addController('c1')
    net.setPropagationModel(model="logNormalShadowingPropagationLossModel", exp=4.5, variance=10)
    info('*** Configuring Wifi Nodes\n')
    net.configureWifiNodes()

    info('*** Associating and creating Links\n')
    net.addLink(ap1, h1)
    net.addLink(sta1, ap1)

    net.plotGraph(max_x=180, max_y=180)
    startime = time.time()
    net.startMobility(time=0)
    net.mobility(sta1, 'start', time=100, position='60,41,0')
    net.mobility(sta1, 'stop', time=199, position='100,41,0')
    net.stopMobility(time=200)

    info('**Starting Network\n')
    net.build()
    c1.start()
    ap1.start([c1])

    time.sleep(3)
    info('Starting iperf host server at 10.0.0.1\n')
    h1.cmd('iperf -s -p 5566 -i 1 &')
    time.sleep(2)
    sta1.cmd('sudo wireshark &')
    time.sleep(2)
    currenttime = time.time()
    difftime = currenttime - startime
    last_distance = 0
    while difftime < 230:
        currenttime = time.time()
        difftime = currenttime - startime
        distance = sta1.get_distance_to(ap1)
        if last_distance == distance:
            continue
        last_distance = distance
        res = sta1.cmd('iperf -c 10.0.0.1 -p 5566 -i 1 -t 1')
        currenttime = time.time()
        difftime = currenttime - startime
        line = res.splitlines()
        throughput = line[-1].split(' ')[-2]
        if throughput == 'to' or throughput == 'in':
            print(throughput)
            print('sta1 is not connected to ap1')
            break
        throughput = float(throughput)
        print('Throughput Value', throughput)
        distance = sta1.get_distance_to(ap1)
        print('Distance', distance)
        throughput_list.append(throughput)
        distance_list.append(distance)

    with open('read.csv', 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(zip(distance_list, throughput_list))

    info('**Stopping network\n')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()


