//#include <TARGET_LPC1768/cmsis.h>

#include "RFManager.h"



RFManager::RFManager(PinName txPinName, PinName rxPinName):

        serial(txPinName, rxPinName), buf(64) {



    messageAvailable = false;

    receiveCounter = 0;

    shortCommandsEnabled = false;

    shortCommandLength = 5;

    longCommandLength = 12;

    commandLength = longCommandLength;



    if (rxPinName == P2_1) {

        serialId = 1;

    } else if (rxPinName == P0_11) {

        serialId = 2;

    } else if (rxPinName == P0_1) {

        serialId = 3;

    } else {

        serialId = 0;

    }



    serial.attach(this, &RFManager::rxHandler);

}



void RFManager::baud(int baudrate) {

    serial.baud(baudrate);

}



void RFManager::rxHandler(void) {

    // Interrupt does not work with RTOS when using standard functions (getc, putc)

    // https://developer.mbed.org/forum/bugs-suggestions/topic/4217/



    while (serial.readable()) {

        char c = serialReadChar();



        if (receiveCounter < commandLength) {

            if (receiveCounter == 0) {

                // Do not continue before a is received

                if (c == 'a') {

                    receiveBuffer[receiveCounter] = c;

                    receiveCounter++;

                }

            } else if (c == 'a' && !shortCommandsEnabled

                || c == 'a' && shortCommandsEnabled && (receiveCounter < commandLength - 1)

            ) {

                // If a is received in the middle, assume some bytes got lost before and start from beginning

                receiveCounter = 0;



                receiveBuffer[receiveCounter] = c;

                receiveCounter++;

            } else {

                receiveBuffer[receiveCounter] = c;

                receiveCounter++;

            }



            if (receiveCounter == commandLength) {

                receiveCounter = 0;



                for (unsigned int i = 0; i < commandLength; i++) {

                    buf.queue(receiveBuffer[i]);

                }



                if (!messageAvailable) {

                    handleMessage();

                    //break;

                }

            }

        }

    }

}



bool RFManager::readable() {

    return messageAvailable;

}



char *RFManager::read() {

    messageAvailable = false;

    return receivedMessage;

}



void RFManager::send(char *sendData) {

    serialWrite(sendData, commandLength);

}



void RFManager::send(char *sendData, int length) {

    serialWrite(sendData, length);

}



void RFManager::update() {

    /*if (receiveCounter == commandLength) {

        handleMessage();

        _callback.call();

    }*/



    if (buf.available() >= commandLength) {

        handleMessage();

    }

}



void RFManager::handleMessage() {

    if (messageAvailable) {

        return;

    }



    for (unsigned int i = 0; i < commandLength; i++) {

        buf.dequeue(receivedMessage + i);

    }



    receivedMessage[commandLength] = '\0';



    /*receiveCounter = 0;



    memcpy(receivedMessage, receiveBuffer, sizeof(receiveBuffer));*/



    messageAvailable = true;

}



void RFManager::serialWrite(char *sendData, int length) {

    int i = 0;



    while (i < length) {

        if (serial.writeable()) {

            serial.putc(sendData[i]);

        }

        i++;

    }

}



char RFManager::serialReadChar() {

    if (serialId == 1) {

        return LPC_UART1->RBR;

    }



    if (serialId == 2) {

        return LPC_UART2->RBR;

    }



    if (serialId == 3) {

        return LPC_UART3->RBR;

    }



    return LPC_UART0->RBR;

}



void RFManager::setShortCommandMode(bool isEnabled) {

    shortCommandsEnabled = isEnabled;

    receiveCounter = 0;



    if (isEnabled) {

        commandLength = shortCommandLength;

    } else {

        commandLength = longCommandLength;

    }

}