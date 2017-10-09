import curses

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

            if keyStroke == ord('1'):
                self.move.drive(self.driveSpeed, -60)

            if keyStroke == ord('2'):
                self.move.drive(self.driveSpeed, 0)

            if keyStroke == ord('s'):
                self.move.drive(self.driveSpeed, 120)

            if keyStroke == ord('s'):
                self.move.drive(self.driveSpeed, -120)

            if keyStroke == ord('a'):
                self.move.rotate(-self.turnSpeed)

            if keyStroke == ord('d'):
                self.move.rotate(self.turnSpeed)

            if keyStroke == ord(' '):
                self.move.brake()
        print("Manual driving deactivated.")
        curses.endwin()