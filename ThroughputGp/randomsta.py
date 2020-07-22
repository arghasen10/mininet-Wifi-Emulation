#!/usr/bin/python

import random, time
from mn_wifi.net import Mininet_wifi
from mininet.log import info, setLogLevel
from mn_wifi.cli import CLI


def topology():
    net = Mininet_wifi()
    info('Creating Nodes\n')
    nodes = {}
    apnodes = {}
    h1 = net.addHost('h1', mac='00:00:00:00:00:01', ip='10.0.0.1')
    for i in range(7):
        nodes['sta%s' % (i+1)] = net.addStation('sta%s' % (i+1), mac='00:00:00:00:00:0%s' % (i+2),
                                                ip='10.0.0.%s' % (i+2), min_x=25, max_x=75, min_y=25, max_y=75,
                                                min_v=1, max_v=1.5)

    ap1 = net.addAccessPoint('ap1', ssid='ap-ssid', mode='n', channel='1', position='20.0,80.0,0.0', range=42)
    ap2 = net.addAccessPoint('ap2', ssid='ap-ssid', mode='n', channel='6', position='80.0,80.0,0.0', range=42)
    ap3 = net.addAccessPoint('ap3', ssid='ap-ssid', mode='n', channel='1', position='80.0,20.0,0.0', range=42)
    ap4 = net.addAccessPoint('ap4', ssid='ap-ssid', mode='n', channel='6', position='20.0,20.0,0.0', range=42)
    c1 = net.addController('c1')
    net.setPropagationModel(model='logNormalShadowingPropagationLossModel', exp=4.5, variance=10)
    info('Configuring Nodes\n')
    net.configureWifiNodes()

    info('Associating and creating links\n')
    net.addLink(h1, ap1)
    net.addLink(ap1, ap2)
    net.addLink(ap2, ap3)
    net.addLink(ap3, ap4)
    net.addLink(ap4, ap1)

    net.plotGraph(min_x=-40, max_x=150, min_y=-40, max_y=150)

    net.setMobilityModel(time=0, model='RandomWalk')
    net.startMobility(time=0, AC='llf')

    net.build()
    c1.start()
    ap1.start([c1])
    ap2.start([c1])
    ap3.start([c1])
    ap4.start([c1])

    time.sleep(5)

    for i in range(7):
        res = nodes['sta%s' % (i+1)].cmd('iw dev sta%s-wlan0 link' % (i+1))
        if res.splitlines()[0].split(' ')[0] == 'Connected':
            if res.splitlines()[0].split(' ')[2].split(':')[-2] in apnodes:
                apnodes[res.splitlines()[0].split(' ')[2].split(':')[-2]].append(i+1)
            else:
                apnodes[res.splitlines()[0].split(' ')[2].split(':')[-2]] = [i+1]
        else:
            print('sta%s is not connected' % (i+1))

    print(apnodes)
    file = open('data.txt', 'w')
    header = "sta Name,Associated AP,thpt,distance_ap1,distance_ap2,distance_ap3,distance_ap4,time\n"
    file.write(header)
    file.close()
    for key in apnodes:
        if len(apnodes[key]) == 2:
            nodes['sta%s' % apnodes[key][0]].cmd('iperf -s -p 5566 -i 1 -t 100 &')
            time.sleep(2)
            startime = time.time()
            currenttime = time.time()
            difftime = currenttime - startime
            while difftime < 90:
                currenttime = time.time()
                difftime = currenttime - startime
                name = 'sta%s' % apnodes[key][1]
                clientdata = nodes[name].cmd('iperf -c 10.0.0.%s -p 5566 -i 1 -t 1' % (apnodes[key][0] + 1))
                print(clientdata)
                thpt = clientdata.splitlines()[-1].split(' ')[-2]
                if thpt == 'to' or thpt == 'in':
                    continue
                dist1 = nodes[name].get_distance_to(ap1)
                dist2 = nodes[name].get_distance_to(ap2)
                dist3 = nodes[name].get_distance_to(ap3)
                dist4 = nodes[name].get_distance_to(ap4)
                associated_to = nodes[name].wintfs[0].associatedTo
                row = name+","+str(associated_to)+","+str(thpt)+","+str(dist1)+","+str(dist2)+","+str(dist3)+","+str(dist4)+","+str(difftime)+"\n"
                file = open('data.txt', 'a')
                file.write(row)
                file.close()


                

    CLI(net)
    info('stopping network\n')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()

