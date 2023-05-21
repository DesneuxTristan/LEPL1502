#include <SPI.h>

#define CS_pin 10
#define Sleep_pin 9
#define SPI_pin 7
#define RsltA_pin 6
#define RsltB_pin 5

void setup() {
  // put your setup code here, to run once:
  pinMode(CS_pin, OUTPUT);
  pinMode(Sleep_pin, OUTPUT);
  pinMode(SPI_pin, OUTPUT);
  pinMode(RsltA_pin, INPUT);
  pinMode(RsltB_pin, INPUT);
  digitalWrite(CS_pin, HIGH);
  digitalWrite(Sleep_pin, LOW);
  digitalWrite(SPI_pin, HIGH);
  Serial.begin(9600);//whatever BAUD rate

}

bool sleepMode(true);
uint8_t switchState(0x00);
uint16_t boardState(0x0000);

void prntBits(uint16_t b)
{
  for(int i = 15; i >= 0; i--)
  {
    Serial.print(bitRead(b,i));
    //if(i % 4 == 0) Serial.print(" ");
  }  
  Serial.println();
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available()>0){
    String com = Serial.readString();
    if(com == "Start"){
      sleepMode = false;
      SPI.begin();
      SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE3));
      digitalWrite(Sleep_pin, HIGH);
    }
    else if(com == "Stop"){
      digitalWrite(Sleep_pin, LOW);
      SPI.endTransaction();
      SPI.end();
      sleepMode = true;
    }
  }

  if(!sleepMode)//check all squares and send if changes
  {
    switchState = 0x01;
    uint16_t newBoardState(0x0000);
    for(unsigned char i(0); i < 8; ++i)
    {
      digitalWrite(CS_pin, LOW);
      SPI.transfer(switchState);
      SPI.transfer(switchState);
      digitalWrite(CS_pin, HIGH);
      switchState <<= 1;

      //update results
      delay(30);
      newBoardState ^= (uint16_t(digitalRead(RsltA_pin)) << (i+8)) ^ (uint16_t(digitalRead(RsltB_pin)) << i);
      newBoardState &= 0xfffe; //Cette ligne permet d'ignorer la bobine disfonctionelle

      //give blank time
      digitalWrite(CS_pin, LOW);
      SPI.transfer16(0xffff);
      digitalWrite(CS_pin, HIGH);
      delay(10);
    }
    if(newBoardState != boardState)
    {
    Serial.write((newBoardState >>8)&0xFF);
    Serial.write(newBoardState & 0xFF);
    //prntBits(newBoardState);
    boardState = newBoardState;
    }
  }
}
