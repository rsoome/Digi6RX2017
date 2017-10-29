import serial

# For listening to referee signals
# TODO: Implement
class RefereeHandler:

    def __init__(self, robotID, fieldID):
        self.robotID = robotID
        self.fieldID = fieldID

    def handleCommand(self, msg):
        print(msg)
        cmd = ""

        if cmd[0] == "a":
            if cmd[1] == self.fieldID:
                if cmd[2] == self.robotID or cmd[2] == "X":
                    endOfMsg = msg.find("-")
                    if endOfMsg != -1:
                        cmd = msg[3:endOfMsg]
                    else:
                        cmd = msg[3:].strip()
        return cmd



