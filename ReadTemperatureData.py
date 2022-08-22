#! python3

import serial
import binascii
import json
import datetime

# The standard Linux serial port
kSerialPort = "/dev/ttyACM0"

# Number of seconds to wait before complaining about not getting a reading
kNoReadingWarning = 600

kSaveFile = "/var/run/temperature-sensor.json"

vLastSuccess = datetime.datetime.now()

vSerial = serial.Serial(kSerialPort, baudrate=9600, timeout=5)

print("Connected to", vSerial.name)
while True:
    vSerialData = vSerial.read_until()
    vSerialLine = vSerialData.decode('utf-8').strip()
    if len(vSerialLine) < 2:
        vDiff = datetime.datetime.now() - vLastSuccess
        if vDiff.total_seconds() > kNoReadingWarning:
            print("It's been {0} seconds since we last got a reading.".format(vDiff.total_seconds()))
        continue

    try:
        vJson = json.loads(vSerialLine)
    except:
        print("Couldn't parse JSON: {0}".format(vSerialLine))
        continue

    if 'crc32' not in vJson:
        print("No 'crc32' checksum found in reading. =(")
        continue

    vCpuTemperature = vJson.get('cpuTempC', None)
    vHumidity = vJson.get('humidity%', None)
    vPressure = vJson.get('pressurehPa', None)
    vSensorTemperature = vJson.get('sensorTempC', None)

    vCRCString = "temp:{0} humd:{1} pres:{2} cpu:{3}".format(
        vSensorTemperature, vHumidity, vPressure, vCpuTemperature)

    # Compute the checksum of the string
    vCRC = hex(binascii.crc32(vCRCString.encode('utf-8')))

    # Check that our CRC's match
    if vCRC != vJson['crc32']:
        print("CRC32 mismatch -- data might be corrupt.")
        print("Computed CRC:  {0}".format(vCRC))
        print("CRC From Data: {1}".format(vCRC, vJson['crc32']))
        continue

    # We got good data!
    vLastSuccess = datetime.datetime.now()
    vJson['lastUpdate'] = int(vLastSuccess.timestamp())
    vJson['lastUpdatePretty'] = vLastSuccess.strftime("%c")
    print(vJson)

    with open(kSaveFile, 'w') as vFD:
        json.dump(vJson, vFD)
    