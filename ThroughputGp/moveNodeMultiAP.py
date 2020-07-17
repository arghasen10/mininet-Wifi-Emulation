#!/usr/bin/python

from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.cli import CLI


def topology():
    net = Mininet_wifi()

    info('**Creating Nodes**\n')
    h1 = net.addHost('h1', mac='00:00:00:00:00:01', ip='10.0.0.1/8')
    sta1 = net.addStation('sta1', mac='00:00:00:00:00:02', ip='10.0.0.2/8', range=20)
    ap1 = net.addAccessPoint('ap1', ssid='api-ssid-1', mode='g', channel='1', position='32,50,0', range=30,)
    ap2 = net.addAccessPoint('ap2', ssid='api-ssid-2', mode='g', channel='6', position='55,50,0', range=30)
    ap3 = net.addAccessPoint('ap3', ssid='api-ssid-3', mode='g', channel='1', position='78,50,0', range=30)
    c1 = net.addController('c1')
    net.setPropagationModel(model="logDistance", exp=4.5)
    info('*** Configuring Wifi Nodes\n')
    net.configureWifiNodes()

    info('*** Associating and creating Links\n')
    net.addLink(ap1, h1)
    net.addLink(ap1, ap2)
    net.addLink(ap2, ap3)

    net.plotGraph(max_x=150, max_y=150)

    net.startMobility(time=0,AC='llf')
    net.mobility(sta1, 'start', time=100, position='22,52,0')
    net.mobility(sta1, 'stop', time=199, position='94,52,0')
    net.stopMobility(time=200)

    info('**Starting Network\n')
    net.build()
    c1.start()
    ap1.start([c1])
    ap2.start([c1])
    ap3.start([c1])

    info('**Running CLI\n')
    CLI(net)

    info('**Stopping network\n')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
