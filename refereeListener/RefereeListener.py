import serial

# For listening to referee signals
# TODO: Implement
class RefereeListener:


    def __init__(self, port, baud):
        self.ser = serial.Serial(port=port, baudrate=baud, timeout=0.8)



