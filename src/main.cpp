#include "Arduino.h"
#include <MFRC522.h>

//HW PIN for MFRC522
#define SS_PIN D2
#define RST_PIN D4

// To be changed if a new reader is configured
// 0x04 for EE-5
// 0x05 für EE-1
#define WORK_PAGE 0x06

byte RBuff[18];
uint8 Page = WORK_PAGE;
byte pACK[] = {0xE, 0x5};
byte PSWBuff[] = {0xFF, 0xAB, 0xBA, 0xFF};
byte WBuff[] = {0x00, 0x00, 0x00, 0x04};

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup()
{
  Serial.begin(115200);
  Serial.setTimeout(100);
  SPI.begin();
  mfrc522.PCD_Init();
  while (Serial.available())
  {
    Serial.read();
  }
}

int ReadCredit(uint8 chippage)
{
  byte buffer[18];
  byte byteCount;
  byteCount = sizeof(buffer);

  mfrc522.PCD_NTAG216_AUTH(&PSWBuff[0], pACK);
  int res = mfrc522.MIFARE_Read(chippage, buffer, &byteCount);

  if (res != 0 || ((buffer[0] + buffer[1] + buffer[2] + buffer[3]) / 4) != (buffer[0] & buffer[1] & buffer[2] & buffer[3]))
  {
    return -1;
  }
  return (buffer[0] + buffer[1] + buffer[2] + buffer[3]) / 4;
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

byte WriteCredit(int newCredit_lokal, uint8 chipPage)
{
  byte WBuff[] = {newCredit_lokal, newCredit_lokal, newCredit_lokal, newCredit_lokal};

  if (!mfrc522.PICC_IsNewCardPresent())
    return 4;

  if (!mfrc522.PICC_ReadCardSerial())
    return 5;

  mfrc522.PCD_NTAG216_AUTH(&PSWBuff[0], pACK);
  return mfrc522.MIFARE_Ultralight_Write(chipPage, WBuff, 4);
}

bool secondInit = true;
void loop()
{

  String cmd = Serial.readString();

  if (cmd == "ping")
  {
    Serial.println("pong");

    cmd = Serial.readString();

    if (secondInit)
    {
      //Problems make problems...
      mfrc522.PCD_Init();
      secondInit = false;
    }

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
      Serial.println(ReadCredit(Page));
    }
    else if (cmd == "GetCardInformation")
    {
      String ID = getID();
      int Credit_1 = ReadCredit(Page);
      Serial.println(ID + "_" + String(Credit_1) + "_" + String(Credit_1));
    }
    else if (cmd.indexOf("WriteCredit") != -1)
    {
      String no = cmd.substring(14);
      String page = cmd.substring(0, 1);
      byte result = WriteCredit(byte(no.toInt()), Page);

      cmd += "_";
      cmd += result;

      Serial.println(cmd);
    }
    else if (cmd.indexOf("Reset") != -1)
    {
      String page = cmd.substring(0, 1);
      byte result = WriteCredit(byte(0), Page);

      cmd += "_";
      cmd += result;

      Serial.println(cmd);
    }
    else if (cmd == "Init")
    {

      while (!mfrc522.PICC_IsNewCardPresent())
      {
      }
      mfrc522.PICC_ReadCardSerial();
      mfrc522.MIFARE_Ultralight_Write(0xE5, PSWBuff, 4);
      mfrc522.MIFARE_Ultralight_Write(0xE6, pACK, 4);
      mfrc522.MIFARE_Ultralight_Write(0xE3, WBuff, 4);
      byte WBuff[] = {0, 0, 0, 0};
      mfrc522.PCD_NTAG216_AUTH(&PSWBuff[0], pACK);
      mfrc522.MIFARE_Ultralight_Write(Page, WBuff, 4);
      Serial.println("OK");
    }
  }
}
