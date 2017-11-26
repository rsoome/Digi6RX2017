# Digi6RX2017

#CURRENT BRANCH USED - line_detectionǐ

Digi6's code for basketball robot  compete in Robotex of 2017

cancellationToken - thread cancellation token for multi threaded image processing. Currently not used.

imageProcessor - classes for image capturing and processing

mainboard firmware - contains the firmware used on the mainboard. Written by Reiko Randoja.

manualDrive - manual control of the robot. Currently extremely buggy.

mbcomm - mainboard communication

movementlogic - contains calculation of speeds and sends movement related commands to mainboard

refereeHandler - handles referee commands

settings - handles reading from and writing settings to file

socketHandler - socket communication package. The robot will send the camera feed and objects' location to the socket and receives various commands from the socket. 

target - definines the targets - balls, baskets and lines

throwingLogic - contains classes for communication with parts of the throwing mechanism - throwing motors and grabber servos. Communication to these parts will e held through this package.

timer - a simple timer for measuring time.

windowHandler - creates and manages windows to display the robot's video feed.

RXmain.py - the main class to be run on the robot

RXmainClient.py - the main class to be run on the client receiving the camera feed and sending commands to the robot.
