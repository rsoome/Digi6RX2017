import curses
import time

class ManualDrive:

    def __init__(self, move, driveSpeed, turnSpeed):
        print("Manual driving activated.")
        self.move = move
        self.driveSpeed = driveSpeed
        self.turnSpeed = turnSpeed

    def run(self):
        screen = curses.initscr()
        curses.cbreak()
        screen.keypad(1)
        curses.noecho()

        keyStroke = ''
        while keyStroke != ord('q'):

            keyStroke = screen.getch()

            while keyStroke == ord('w'):
                self.move.drive(self.driveSpeed, 0, ), None,
                keyStroke = self.getKeystroke(screen)

            while keyStroke == ord('2'):
                self.move.drive(self.driveSpeed, 60, ), None,
                keyStroke = self.getKeystroke(screen)

            while keyStroke == ord('s'):
                self.move.drive(self.driveSpeed, 180, ), None,
                keyStroke = self.getKeystroke(screen)

            while keyStroke == ord('1'):
                self.move.drive(self.driveSpeed, -60, ), None,
                keyStroke = self.getKeystroke(screen)

            while keyStroke == ord('a'):
                self.move.rotate(-self.turnSpeed)
                keyStroke = self.getKeystroke(screen)

            while keyStroke == ord('d'):
                self.move.rotate(self.turnSpeed)
                keyStroke = self.getKeystroke(screen)

            while keyStroke == ord(' '):
                self.move.brake()
                keyStroke = self.getKeystroke(screen)

            self.move.mb.sendValues()

        print("Manual driving deactivated.")
        curses.endwin()

    def getKeystroke(self, screen):
        keyStroke = ''
        keyStroke = screen.getch()
        return keyStroke