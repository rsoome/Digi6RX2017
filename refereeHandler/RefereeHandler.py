import serial

# For listening to referee signals
# TODO: Implement
class RefereeHandler:

    def __init__(self, robotID, fieldID, mb):
        self.robotID = robotID
        self.fieldID = fieldID
        self.mb = mb

    def handleCommand(self, msg):
        cmd = ""

        if msg[0] == "a":
            if msg[1] == self.fieldID:
                if msg[2] == self.robotID or msg[2] == "X":
                    if msg[2] == self.robotID:
                        self.sendAck()
                    endOfMsg = msg.find("-")
                    if endOfMsg != -1:
                        cmd = msg[3:endOfMsg]
                    else:
                        cmd = msg[3:].strip()
        return cmd

    def sendAck(self):
        self.mb.sendRFMessage("a" + self.fieldID + self.robotID + "ACK-----")



