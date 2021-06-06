#!/usr/bin/bash
# Start WiFi HotSpot on Boot
service call wifi 37 i32 0 i32 1

export PASSIVE="0"
exec ./launch_chffrplus.sh

