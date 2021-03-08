#include "Arduino.h"
#include <MFRC522.h>

#define SS_PIN          D2         
#define RST_PIN         D4      
#define YOUR_PAGE       0x5

MFRC522 mfrc522(SS_PIN, RST_PIN); 

byte PSWBuff[] = {0xFF, 0xAB, 0xBA, 0xFF};
byte pACK[] = {0xE, 0x5};
byte WBuff[] = {0x00, 0x00, 0x00, 0x04};
byte RBuff[18];
uint8 Page = YOUR_PAGE;

int ReadCredit()
{
  byte buffer[18];
  byte byteCount;
  byteCount = sizeof(buffer);
  int res = mfrc522.MIFARE_Read(Page, buffer, &byteCount);
  //Serial.println(buffer[0]);
  //Serial.println(buffer[1]);
  //Serial.println(buffer[2]);
  //Serial.println(buffer[3]);
  if (res != 0 || ((buffer[0]+buffer[1]+buffer[2]+buffer[3])/4) != (buffer[0] & buffer[1] & buffer[2] & buffer[3]))
  {
    return -1;
  }
  return (buffer[0]+buffer[1]+buffer[2]+buffer[3])/4; 
}

String getID()
{
  long code = 0;

  if (mfrc522.PICC_ReadCardSerial())
  {
    for (byte i = 0; i < mfrc522.uid.size; i++)
    {
      code = ((code + mfrc522.uid.uidByte[i]) * 10);
    }
  }
  return String(code, DEC);
}

int WriteCredit(int newCredit_lokal)
{
  byte WBuff[] = {newCredit_lokal, newCredit_lokal, newCredit_lokal, newCredit_lokal};
  mfrc522.PCD_NTAG216_AUTH(&PSWBuff[0], pACK);
  mfrc522.MIFARE_Ultralight_Write(Page, WBuff, 4); 
  //Serial.println(newCredit_lokal);
  return 1;
}

void setup()
{
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  while(Serial.available()){Serial.read();}
}

void loop()
{

  String cmd =  Serial.readString();
  Serial.println("Received: " + cmd);

  if (cmd == "IsNewCardPresent")
  {
    Serial.println(mfrc522.PICC_IsNewCardPresent());
  }
  else if (cmd == "getID")
  {
    Serial.println(getID());
  }
  else if (cmd == "ReadCredit")
  {
    Serial.println(ReadCredit());
  }
  else if (cmd == "WriteCredit")
  {
    Serial.println("Input:");
    String Nr = Serial.readString();
    Serial.println(WriteCredit(Nr.toInt()));
  }
  else if (cmd == "Reset")
  {
    while(!mfrc522.PICC_IsNewCardPresent()){}
      mfrc522.PICC_ReadCardSerial();
      ReadCredit();
      Serial.println("Reset");
      

      int flag = 0;

      flag = mfrc522.MIFARE_Ultralight_Write(0xE5, PSWBuff, 4);
      mfrc522.MIFARE_Ultralight_Write(0xE6, pACK, 4);
      mfrc522.MIFARE_Ultralight_Write(0xE3, WBuff, 4);

      WriteCredit(0);

      ReadCredit();

      if (flag == 3)
      {
        delay(2000);
        Serial.println("Err");
      }

      bool flagNow = true;
      bool flagPast = false;

      while (true)
      {
        flagPast = flagNow;
        flagNow = mfrc522.PICC_IsNewCardPresent();
        if (flagNow == flagPast)
          break;
        
        WriteCredit(0);
        Serial.println("Done!");
      }
  }
  else
  {
    Serial.println("Unknown cmd");
  }
}
