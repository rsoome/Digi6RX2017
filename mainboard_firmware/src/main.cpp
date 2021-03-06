#include "mbed.h"
#include "pins.h"
#include "RGBLed/RGBLed.hpp"
#include "USBSerial.h"
#include "motor/motor.h"
#include "RFManager.h"

USBSerial serial;

Serial pc(USBTX, USBRX);
//Serial com(COMTX, COMRX);

RGBLed led1(LED1R, LED1G, LED1B);
RGBLed led2(LED2R, LED2G, LED2B);

DigitalIn infrared(P2_12);

#define NUMBER_OF_MOTORS 4
#define GRABBER_MAX_PWM 2350
#define GRABBER_MIN_PWM 550
#define GRABBER_CONSTANT (GRABBER_MAX_PWM + GRABBER_MIN_PWM)

Motor motor0(&pc, M0_PWM, M0_DIR1, M0_DIR2, M0_FAULT, M0_ENCA, M0_ENCB);
Motor motor1(&pc, M1_PWM, M1_DIR1, M1_DIR2, M1_FAULT, M1_ENCA, M1_ENCB);
Motor motor2(&pc, M2_PWM, M2_DIR1, M2_DIR2, M2_FAULT, M2_ENCA, M2_ENCB);
//Motor motor3(&pc, M3_PWM, M3_DIR1, M3_DIR2, M3_FAULT, M3_ENCA, M3_ENCB);

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

RFManager rfModule(COMTX, COMRX);

void serialInterrupt();
void parseCommand(char *command);

Ticker pidTicker;
int pidTickerCount = 0;
static const float PID_FREQ = 60;

char buf[32];
int serialCount = 0;
bool serialData = false;

bool failSafeEnabled = true;
bool failDeadlyEnabled = false;
int ticksSinceCommand = 0;

void pidTick() {
  motor0.pidTick();
  motor1.pidTick();
  motor2.pidTick();
//  motor3.pidTick();

  if (pidTickerCount++ % 25 == 0) {
    led1.setBlue(!led1.getBlue());
  }

  // Fail-safe
  if (failSafeEnabled || failDeadlyEnabled) {
    ticksSinceCommand++;
  }

  if (ticksSinceCommand == 60) {
    if (failSafeEnabled){
        motor0.setSpeed(0);
        motor1.setSpeed(0);
        motor2.setSpeed(0);
        //motor3.setSpeed(0);
    }

    /*if (failDeadlyEnabled){
        motor0.setSpeed(100);
        motor1.setSpeed(100);
        motor2.setSpeed(100);
        //motor3.setSpeed(0);
    }*/

    m3.pulsewidth_us(100);
  }

}

int main() {

  pwm0.pulsewidth_us(GRABBER_MAX_PWM);
  pwm1.pulsewidth_us(GRABBER_MIN_PWM);

  if (rfModule.readable()) {

        serial.printf("ref:%s\n", rfModule.read());

    }



    rfModule.update();

  pidTicker.attach(pidTick, 1/PID_FREQ);
  //serial.attach(&serialInterrupt);

  // Ball detector status
  int infraredStatus = -1;

  // Dribbler motor
  //m3.period_us(400);
  m3.pulsewidth_us(100);

  while (1) {

    if (rfModule.readable()) {
         serial.printf("ref:%s\n", rfModule.read());
     }

    rfModule.update();

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


      if (newInfraredStatus) {
        led2.set(RGBLed::White);
      } else {
        led2.set(RGBLed::Black);
      }

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

    serial.printf("%d:%d:%d\n", motor0.getSpeed(), motor1.getSpeed(), motor2.getSpeed());
  }

  //Servo range: 545...2350
  else if (command[0] == 's' && command[1] == 's') {
    int servoValue;

    servoValue = atoi(command + 2);
    if (servoValue < GRABBER_MIN_PWM) servoValue = GRABBER_MIN_PWM;
    if (servoValue > GRABBER_MAX_PWM) servoValue = GRABBER_MAX_PWM;
    pwm0.pulsewidth_us(servoValue);
    pwm1.pulsewidth_us(GRABBER_CONSTANT - servoValue);
  }

  else if (command[0] == 'd') {
      m3.pulsewidth_us(atoi(command + 1));
  }

  if (command[0] == 'r' && command[1] == 'f') {
      rfModule.send(command + 2);
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
    failDeadlyEnabled = false;
  }

  else if (command[0] == 'f' && command[2] == 'd') {
    failSafeEnabled = false;
    failDeadlyEnabled = command[2] == '1';
  }
}
