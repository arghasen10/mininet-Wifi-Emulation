#!/usr/bin/python

from mininet.node import Controller, OVSKernelSwitch, Host
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import Station, OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference
from subprocess import call


def myNetwork():

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
    ap1 = net.addAccessPoint('ap1', cls=OVSKernelAP, ssid='ap1-ssid',
                             channel='1', mode='n', failMode='standalone', position='20.0,80.0,0.0', range=42)
    ap2 = net.addAccessPoint('ap2', cls=OVSKernelAP, ssid='ap2-ssid',
                             channel='6', mode='n', failMode='standalone', position='80.0,80.0,0.0', range=42)
    ap3 = net.addAccessPoint('ap3', cls=OVSKernelAP, ssid='ap3-ssid',
                             channel='1', mode='n', failMode='standalone', position='80.0,20.0,0.0', range=42)
    ap4 = net.addAccessPoint('ap4', cls=OVSKernelAP, ssid='ap4-ssid',
                             channel='6', mode='n', failMode='standalone', position='20.0,20.0,0.0', range=42)

    info('*** Add hosts/stations\n')
    nodes = {}
    for i in range(7):
        nodes['sta%s' % (i+1)] = net.addStation('sta%s' % (i+1),
                                                ip='10.0.0.%s/8' % (i+2), min_x=25, max_x=75, min_y=25, max_y=75,
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

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    myNetwork()

