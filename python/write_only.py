import serial.tools.list_ports


def IsNewCardPresent():
    Serial.flushOutput()
    Serial.write(b'IsNewCardPresent')
    _ans = Serial.readline().decode().replace("\n", "").replace("\r", "")
    if 'IsNewCardPresent' in _ans:
        return Serial.readline().decode().replace("\n", "").replace("\r", "")

    else:
        return -1


def getId():
    Serial.flushOutput()
    Serial.flushInput()
    Serial.write(b'getID')
    _ans = Serial.readline().decode().replace("\n", "").replace("\r", "")
    if 'getID' in _ans:
        ID = Serial.readline().decode().replace("\n", "").replace("\r", "")
        Serial.flushOutput()
        Serial.flushInput()
        return ID
    else:
        Serial.flushOutput()
        Serial.flushInput()
        return -1


def ReadCredit():
    Serial.flushOutput()
    Serial.flushInput()
    Serial.write(b'ReadCredit')
    _ans = Serial.readline().decode().replace("\n", "").replace("\r", "")
    if 'ReadCredit' in _ans:
        credit = Serial.readline().decode().replace("\n", "").replace("\r", "")
        Serial.flushOutput()
        Serial.flushInput()
        return credit
    else:
        Serial.flushOutput()
        Serial.flushInput()
        return -1


def WriteCredit(number):
    Serial.flushOutput()
    Serial.flushInput()
    Serial.write(b'WriteCredit')

    _ans = Serial.readline().decode().replace("\n", "").replace("\r", "")
    if 'WriteCredit' in _ans:
        reply = Serial.readline().decode().replace("\n", "").replace("\r", "")
        if "Input:" in reply:
            print("Writer is wating for input...")
            Serial.flushOutput()
            Serial.flushInput()
            Serial.write(number.encode())
            res_write = Serial.readline().decode().replace("\n", "").replace("\r", "")
            #print("Wrote " + str(res_write) + " to card")
            return res_write
    else:
        Serial.flushOutput()
        Serial.flushInput()
        return -1


def flush_serial():
    Serial.flushInput()
    Serial.flushOutput()


def reset_card():
    Serial.flushOutput()
    Serial.flushInput()
    Serial.write(b'Reset')
    _ans = Serial.readline().decode().replace("\n", "").replace("\r", "")
    print(_ans)
    if 'Reset' in _ans:
        Ans = Serial.readline().decode().replace("\n", "").replace("\r", "")
        if 'Reset' in Ans: print("Trying to reset the chip!")
        State = Serial.readline().decode().replace("\n", "").replace("\r", "")
        print(State)
        if 'Err' in State:
            print("Reset Failed !")
            return -1

        Serial.flushOutput()
        Serial.flushInput()
        return 1
    else:
        Serial.flushOutput()
        Serial.flushInput()
        return -1


def read_default():
    Serial.readline().decode()
    print("Clear input and output buffer")

credit = 0


print("K20 - Terminal\n")

ports = serial.tools.list_ports.comports()
PortCount = 0

for port in ports:
    print(str(PortCount) + ": " + port.device)
    PortCount += 1

Count = int(input("\nChoose: "))

print("connect to: " + ports[Count].device + "\n")
Serial = serial.Serial(ports[Count].device)
read_default()

print("## Please place chip on reader ##")

while True:

    Serial.flushInput()
    Serial.flushOutput()
    state = IsNewCardPresent()
    credit = 0

    if state == (" " or "" or not "1"):
        continue

    if state == 'Unknown cmd':
        print("Unkown serial answer - Reset loop")
        flush_serial()
        continue

    if state == "1":

        User_ID = getId()
        current_credit = ReadCredit()

        print("------------------------")
        print("ID:     " + str(User_ID))
        print("Credit: " + str(current_credit))
        print("------------------------")

        if str(current_credit) == "-1":
            print("Card not initialized !")
            ini = int(input("Initialize [0] // Try again [1]: "))
            if ini != 1:
                if reset_card() != 1:
                    print("## Could not reset placed chip ##")
                    continue
                else:
                    print("## Chip reset successful ##")
                    continue
            else:
                continue

        while True:

            mode = input('1 - 30ct\n2 - 50ct\n3 - Setup new chip\n4 - Service\nSelect: ')

            if mode == "1":
                money = float(input("Money: "))
                credit = int(money / 0.30 + int(current_credit))
                break

            elif mode == "2":
                money = float(input("Money: "))
                credit = int(money / 0.50 + int(current_credit))
                break

            elif mode == "3":
                select = "Y"
                if int(current_credit) != 0:
                    print("Credit found on chip!")
                    print("Reset and write 0 to card?")
                    select = str(input("[Y]es [N]o :"))
                if select.upper() == "Y":
                    print("## Reset card ##")
                    while reset_card() != 1:
                        flush_serial()
                        print("Trying to reset you chip !")
                        continue
                else:
                    credit = 0
                break

            elif mode == "4":
                credit = int(input("Service Credit: "))
                break

            else:
                print("## Err - Try again ##")
                continue

        flush_serial()

        print("Write " + str(credit) + " to card")

        write_state = WriteCredit(str(credit))

        flush_serial()
        i = 0
        while True:

            if IsNewCardPresent() == "1":
                break

            i = i + 1

            print("Checking :" + str(i))
            flush_serial()
            if (i > 5):
                break

        flush_serial()

        print("Read new credit: " + ReadCredit())

        if input("Add more? [Y]es [N]o: ").upper() == "Y":
            print("## Please place chip on reader ##")
            continue
        else:
            break

Serial.close()
