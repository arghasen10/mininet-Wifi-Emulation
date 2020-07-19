#!/usr/bin/python

import random
from mn_wifi.net import Mininet_wifi
from mininet.log import info, setLogLevel
from mn_wifi.cli import CLI


def topology():
    net = Mininet_wifi()
    info('Creating Nodes\n')
    nodes = {}
    for i in range(10):
        nodes['sta%s' % (i+1)] = net.addStation('sta%s' % (i+1), mac='00:00:00:00:00:0%s' % (i+1),
                                                ip='10.0.0.%s' % (i+1), min_x=25, max_x=75, min_y=25, max_y=75, min_v=1,
                                                max_v=5)

    ap1 = net.addAccessPoint('ap1', ssid='ap-ssid', mode='g', channel='1', position='20.0,20.0,0.0', range=30)
    ap2 = net.addAccessPoint('ap2', ssid='ap-ssid', mode='g', channel='6', position='20.0,80.0,0.0', range=30)
    ap3 = net.addAccessPoint('ap3', ssid='ap-ssid', mode='g', channel='6', position='80.0,80.0,0.0', range=30)
    ap4 = net.addAccessPoint('ap4', ssid='ap-ssid', mode='g', channel='1', position='80.0,20.0,0.0', range=30)
    c1 = net.addController('c1')
    net.setPropagationModel(model='logNormalShadowingPropagationLossModel', exp=3.5, variance=10)
    info('Configuring Nodes\n')
    net.configureWifiNodes()

    info('Associating and creating links\n')
    net.addLink(ap1, ap2)
    net.addLink(ap2, ap3)
    net.addLink(ap3, ap4)
    net.addLink(ap4, ap1)

    net.plotGraph(min_x=-20, max_x=120, min_y=-20, max_y=120)

    net.setMobilityModel(time=0, model='RandomDirection', max_x=100, max_y=100, seed=20)
    net.build()
    c1.start()
    ap1.start([c1])
    ap2.start([c1])
    ap3.start([c1])
    ap4.start([c1])

    CLI(net)


if __name__ == '__main__':
    setLogLevel('info')
    topology()

