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
                print(keyStroke)
                self.move.drive(self.driveSpeed, 0)
                keyStroke = screen.getch()

            while keyStroke == ord('2'):
                self.move.drive(self.driveSpeed, 60)
                keyStroke = screen.getch()

            while keyStroke == ord('s'):
                self.move.drive(self.driveSpeed, 180)
                keyStroke = screen.getch()

            while keyStroke == ord('1'):
                self.move.drive(self.driveSpeed, -60)
                keyStroke = screen.getch()

            while keyStroke == ord('a'):
                self.move.rotate(-self.turnSpeed)
                keyStroke = screen.getch()

            while keyStroke == ord('d'):
                self.move.rotate(self.turnSpeed)
                keyStroke = screen.getch()

            while keyStroke == ord(' '):
                self.move.brake()
                keyStroke = screen.getch()

            self.move.rotate(0)

        print("Manual driving deactivated.")
        curses.endwin()