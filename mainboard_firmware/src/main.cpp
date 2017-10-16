#include "mbed.h"
#include "pins.h"
#include "RGBLed/RGBLed.hpp"
#include "USBSerial.h"
#include "motor/motor.h"

USBSerial serial;

Serial pc(USBTX, USBRX);
Serial com(COMTX, COMRX);

RGBLed led1(LED1R, LED1G, LED1B);
RGBLed led2(LED2R, LED2G, LED2B);

DigitalIn infrared(ADC0);

#define NUMBER_OF_MOTORS 4

Motor motor0(&pc, M0_PWM, M0_DIR1, M0_DIR2, M0_FAULT, M0_ENCA, M0_ENCB);
Motor motor1(&pc, M1_PWM, M1_DIR1, M1_DIR2, M1_FAULT, M1_ENCA, M1_ENCB);
Motor motor2(&pc, M2_PWM, M2_DIR1, M2_DIR2, M2_FAULT, M2_ENCA, M2_ENCB);
Motor motor3(&pc, M3_PWM, M3_DIR1, M3_DIR2, M3_FAULT, M3_ENCA, M3_ENCB);

/*Motor motors[NUMBER_OF_MOTORS] = {
  Motor(&pc, M0_PWM, M0_DIR1, M0_DIR2, M0_FAULT, M0_ENCA, M0_ENCB),
  Motor(&pc, M1_PWM, M1_DIR1, M1_DIR2, M1_FAULT, M1_ENCA, M1_ENCB),
  Motor(&pc, M2_PWM, M2_DIR1, M2_DIR2, M2_FAULT, M2_ENCA, M2_ENCB),
  Motor(&pc, M3_PWM, M3_DIR1, M3_DIR2, M3_FAULT, M3_ENCA, M3_ENCB)
};*/

PwmOut m0(M0_PWM);
PwmOut m1(M1_PWM);
PwmOut m2(M2_PWM);
PwmOut m3(M3_PWM);
PwmOut pwm0(PWM0);
PwmOut pwm1(PWM1);

void serialInterrupt();
void parseCommand(char *command);

Ticker pidTicker;
int pidTickerCount = 0;
static const float PID_FREQ = 60;

char buf[32];
int serialCount = 0;
bool serialData = false;

bool failSafeEnabled = true;
int ticksSinceCommand = 0;

void pidTick() {
  motor0.pidTick();
  motor1.pidTick();
  motor2.pidTick();
  motor3.pidTick();

  if (pidTickerCount++ % 25 == 0) {
    led1.setBlue(!led1.getBlue());
  }

  // Fail-safe
  if (failSafeEnabled) {
    ticksSinceCommand++;
  }

  if (ticksSinceCommand == 60) {
    motor0.setSpeed(0);
    motor1.setSpeed(0);
    motor2.setSpeed(0);
    motor3.setSpeed(0);

    pwm1.pulsewidth_us(100);
  }

}

int main() {
  pidTicker.attach(pidTick, 1/PID_FREQ);
  //serial.attach(&serialInterrupt);

  // Ball detector status
  int infraredStatus = -1;

  // Dribbler motor
  pwm1.period_us(400);
  pwm1.pulsewidth_us(100);

  while (1) {
    if (serial.readable()) {
      buf[serialCount] = serial.getc();
      //serial.putc(buf[serialCount]);

      if (buf[serialCount] == '\n') {
        parseCommand(buf);
        serialCount = 0;
        memset(buf, 0, 32);
      } else {
        serialCount++;
      }
    }

    /// INFRARED DETECTOR
    int newInfraredStatus = infrared.read();

    if (newInfraredStatus != infraredStatus) {
      infraredStatus = newInfraredStatus;
      serial.printf("i%d\n", newInfraredStatus);
      led2.setGreen(infraredStatus);
    }

    /// COILGUN
    //serial.printf("%d\n", chargerDone.read());
  }
}

void parseCommand(char *command) {
  ticksSinceCommand = 0;

  // command == "sd14:16:10:30"
  if (command[0] == 's' && command[1] == 'd') {
    char * sd;

    sd = strtok(command + 2, ":");
    motor0.setSpeed((int16_t) atoi(sd));

    sd = strtok(NULL, ":");
    motor1.setSpeed((int16_t) atoi(sd));

    sd = strtok(NULL, ":");
    motor2.setSpeed((int16_t) atoi(sd));
  }

  else if (command[0] == 's' && command[1] == 'r') {
    char * sd;

    sd = command + 2
    motor3.setSpeed((int16_t) atoi(sd));
  }

  else if (command[0] == 'd') {
    /*
    if (command[1] == '0') {
      pwm1.pulsewidth_us(100);
    } else if (command[1] == '1') {
      pwm1.pulsewidth_us(268);
    } else*/ {
      pwm1.pulsewidth_us(atoi(command + 1));
    }
    //pwm1.pulsewidth_us((int) atoi(command+1));
    //serial.printf("sending %d\n", (int) atoi(command+1));
  }

  else if (command[0] == 's' && command[1] == 'g') {
    serial.printf("%d:%d:%d\n", motor0.getSpeed(), motor1.getSpeed(), motor2.getSpeed());
  }

  else if (command[0] == 'r') {
    led1.setRed(!led1.getRed());
  }

  else if (command[0] == 'g') {
    led1.setGreen(!led1.getGreen());
  }

  else if (command[0] == 'b') {
    led1.setBlue(!led1.getBlue());
  }

  else if (command[0] == 'i') {
    serial.printf("i%d\n", infrared.read());
  }

  else if (command[0] == 'f') {
    failSafeEnabled = command[1] == '1';
  }
}
