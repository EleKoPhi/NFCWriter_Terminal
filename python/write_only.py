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


print("K20 - Terminal\n")

ports = serial.tools.list_ports.comports()
PortCount = 0

for port in ports:
    print(str(PortCount) + ": " + port.device)
    PortCount += 1

Count = int(input("\nChoose: "))

print("connect to: " + ports[Count].device)
Serial = serial.Serial(ports[Count].device)
read_default()

print("Karte auflegen")

while True:
    Serial.flushInput()
    Serial.flushOutput()

    state = IsNewCardPresent()


    if state == (" " or "" or not "1"): continue

    if state == 'Unknown cmd':
        #print("Err in serial connection - retry")
        flush_serial()
        continue

    if state == "1":

        User_ID = getId()
        current_credit = ReadCredit()

        print("ID:     " + str(User_ID))
        print("Credit: " + str(current_credit))
        print("")

        if str(current_credit) == "-1":
            print("Card not initialized !")
            ini = int(input("Initialize(0) // Try again(1): "))
            if ini is not 1:
                if reset_card() is not 1:
                    print("Let's try again...")
                    continue
                else:
                    print("Passed - Let's try again")
                    continue
            else:
                continue

        while True:

            mode = input('1 - 30ct, 2 - 50ct, Setup new card - 3, 4 - Service: ')

            if mode == "1":
                money = float(input("Money: "))
                credit = int(money / 0.30 + int(current_credit))
                break

            elif mode == "2":
                money = float(input("Money: "))
                credit = int(money / 0.50 + int(current_credit))
                break

            elif mode == "3":
                if int(current_credit) is not 0:
                    print("There is some credit?")
                    print("Reset and write 0 to crad?")
                    select = str(input("YES - 1, NO - 2"))
                if select == "2":
                    credit = int(money / 0.50 + int(current_credit))
                else:
                    credit = 0

                break

            elif mode == "4":
                credit = int(input("Service Credit: "))
                break

            else:
                print("Err - Try again")
                continue

        flush_serial()

        Count = 0

        if select == "1":
            while reset_card() is not 1:
                flush_serial()
                Count+=1
                if Count > 10:
                    print("Could not reset card :(")
                    break
        
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

        if input("Add more? [y][n]") == "y":
            continue
        else:
            break

Serial.close()
