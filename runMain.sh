#!/bin/bash

#                     brightness (int)    : min=0 max=255 step=1 default=0 value=0 flags=slider
#                       contrast (int)    : min=0 max=255 step=1 default=32 value=32 flags=slider
#                     saturation (int)    : min=0 max=255 step=1 default=64 value=64 flags=slider
#                            hue (int)    : min=-90 max=90 step=1 default=0 value=0 flags=slider
#        white_balance_automatic (bool)   : default=1 value=1
#                       exposure (int)    : min=0 max=255 step=1 default=120 value=120 flags=inactive, volatile
#                 gain_automatic (bool)   : default=1 value=1 flags=update
#                           gain (int)    : min=0 max=63 step=1 default=20 value=20 flags=inactive, volatile
#                horizontal_flip (bool)   : default=0 value=0
#                  vertical_flip (bool)   : default=0 value=0
#           power_line_frequency (menu)   : min=0 max=1 default=0 value=0
#                      sharpness (int)    : min=0 max=63 step=1 default=0 value=0 flags=slider


BRIGHTNESS_DEFAULT=0
CONTRAST_DEFAULT=32
SATURATION_DEFAULT=64
HUE_DEFAULT=0
EXPOSURE_DEFAULT=120
GAIN_DEFAULT=20
SHARPNESS_DEFAULT=0

BRIGHTNESS=15
CONTRAST=34
SATURATION=109
HUE=68
EXPOSURE=120
GAIN=14
SHARPNESS=63
POWER_LINE_FREQUENCY=0

echo "Closing Teamviewer daemon"
#sudo teamviewer --daemon stop

echo "Setting up camera."
sudo v4l2-ctl -c gain_automatic=0
sudo v4l2-ctl -c white_balance_automatic=0
sudo v4l2-ctl -c brightness=$BRIGHTNESS
sudo v4l2-ctl -c contrast=$CONTRAST
sudo v4l2-ctl -c saturation=$SATURATION
sudo v4l2-ctl -c hue=$HUE
sudo v4l2-ctl -c exposure=$EXPOSURE
sudo v4l2-ctl -c gain=$GAIN
sudo v4l2-ctl -c sharpness=$SHARPNESS
sudo v4l2-ctl -c power_line_frequency=$POWER_LINE_FREQUENCY

echo "Starting robotex main"
sudo /home/digi6/.virtualenvs/robotex/bin/python3 ./RXmain.py

echo "Starting teamviewer daemon"
#sudo teamviewer --daemon start

echo "Restoring camera settings"
sudo v4l2-ctl -c gain_automatic=1
sudo v4l2-ctl -c white_balance_automatic=1
sudo v4l2-ctl -c brightness=$BRIGHTNESS_DEFAULT
sudo v4l2-ctl -c contrast=$CONTRAST_DEFAULT
sudo v4l2-ctl -c saturation=$SATURATION_DEFAULT
sudo v4l2-ctl -c hue=$HUE_DEFAULT
sudo v4l2-ctl -c exposure=$EXPOSURE_DEFAULT
sudo v4l2-ctl -c gain=$GAIN 
sudo v4l2-ctl -c sharpness=$SHARPNESS_DEFAULT

sudo chmod 666 conf

echo "Done"
