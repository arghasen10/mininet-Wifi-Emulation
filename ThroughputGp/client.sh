#!/bin/bash

xhost +
sudo -u foo -i <<EOF
unset http_proxy
unset https_proxy

set -x
export DISPLAY=:0
firefox http://10.0.0.1:9000
EOF