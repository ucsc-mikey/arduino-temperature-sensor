# This code is written for an Adafruit ESP32-S2 Feather w/ BME280
# https://www.adafruit.com/product/5303

# Using CircuitPython 7.3.1
# https://circuitpython.org/board/adafruit_feather_esp32s2/

import time
import binascii
import json
import board
import microcontroller
from adafruit_bme280 import basic as adafruit_bme280

# Create sensor objects, using the board's default I2C bus.
i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# change this to match your location's pressure (hPa) at sea level
bme280.sea_level_pressure = 1013.25

while True:
    # Make all of our readings pretty
    vSensorTempString = "{0:.2f}".format(bme280.temperature)
    vHumdString = "{0:.1f}".format(bme280.relative_humidity)
    vPressureString = "{0:.1f}".format(bme280.pressure)
    vCpuTempString = "{0:.1f}".format(microcontroller.cpu.temperature)

    # Make a single string we can checksum
    vCRCString = "temp:{0} humd:{1} pres:{2} cpu:{3}".format(
        vSensorTempString, vHumdString, vPressureString, vCpuTempString)

    # Compute the checksum of the string
    vCRC = hex(binascii.crc32(vCRCString.encode('utf-8')))

    # Form a dictionary
    vData = {
        "sensorTempC":vSensorTempString,
        "humidity%":vHumdString,
        "pressurehPa":vPressureString,
        "cpuTempC":vCpuTempString,
        "crc32":vCRC
    }

    # Print out our data as JSON on the serial console
    print(json.dumps(vData))

    # Sleep for a minute
    time.sleep(60)
