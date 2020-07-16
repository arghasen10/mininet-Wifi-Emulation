#!/usr/bin/python

from mininet.log import setLogLevel,info
from mn_wifi.net import Mininet_wifi
from mn_wifi.cli import CLI


def topology():
    net = Mininet_wifi()

    info('**Creating Nodes**\n')
    h1 = net.addHost('h1', mac='00:00:00:00:00:01', ip='10.0.0.1/8')
    sta1 = net.addStation('sta1', mac='00:00:00:00:00:02', ip='10.0.0.2/8', range=20)
    ap1 = net.addAccessPoint('ap1', ssid='api-ssid', mode='g', channel='1', position='80,40,0', range=30)
    c1 = net.addController('c1')
    net.setPropagationModel(model="logDistance", exp=4.5)
    info('*** Configuring Wifi Nodes\n')
    net.configureWifiNodes()

    info('*** Associating and creating Links\n')
    net.addLink(ap1, h1)
    net.addLink(sta1, ap1)

    net.plotGraph(max_x=180, max_y=180)

    net.startMobility(time=0)
    net.mobility(sta1, 'start', time=60, position='20,50,0')
    net.mobility(sta1,'stop', time=119, position='140,50,0')
    net.stopMobility(time=120)

    info('**Starting Network\n')
    net.build()
    c1.start()
    ap1.start([c1])

    info('**Running CLI\n')
    CLI(net)

    info('**Stopping network\n')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
