import serial
import json
import csv
import random
import datetime

# current * 0.1
# power * 10
import sys
import select

#arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)
data_final = []
data_final.append(["hour", "voltage", "current", "power"])


def getRandomChar():
    x = random.randint(48,109)
    if x > 57:
        x = x + 7
    if x > 90:
        x = x + 6
    return (chr)(x)
id = getRandomChar() + getRandomChar() + getRandomChar() + getRandomChar()
print(id)

# def write_read(x):
#     arduino.write(bytes("fdx", 'utf-8'))
#     time.sleep(0.05)
#     data = arduino.readline()
#     return data
while True:
    # num = input("Enter a number: ") # Taking input from user
    # value = write_read(num)
    # print(value)
    data = arduino.readline()
    if data:
        print(data)
        data_json = json.loads(data)
        # if "action" in data_json:
        #     if data_json["action"] == "alive":
        #         arduino.write(bytes("ok", 'utf-8'))
        #     if data_json["action"] == "start":
        #         id = getRandomChar() + getRandomChar() + getRandomChar() + getRandomChar()
        #         arduino.write(bytes(id, 'utf-8'))
        #     elif data_json["action"] == "end":
        #         with open('./data/' + id + '.csv', 'w', newline='') as file:
        #             writer = csv.writer(file)
        #             writer.writerows(data_final)
        #         data_final = []
        #   
        #       data_final.append(["hour", "voltage", "current", "power"])
        # else:
        now = datetime.datetime.now()
        data_final.append([now.strftime("%H:%M:%S"), data_json["voltage"], data_json["current"]*0.1, data_json["power"]*10])
        with open('./data/' + id + '.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data_final)
