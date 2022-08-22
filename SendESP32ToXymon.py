#! /bin/python3.6

import time, sys, json, os, datetime, traceback

import XymonStatus

vColumnName = "esp32_sensors"
vStatusFile = "/var/run/temperature-sensor.json"

vStatusFileErrorColor = XymonStatus.CLEAR

vXymon = XymonStatus.Host(vColumnName)

def PrettyTime(vDirtySeconds):
    vSeconds = int(vDirtySeconds)

    vDays = vSeconds // 86400
    vHours = (vSeconds - (vDays * 86400)) // 3600
    vMins = (vSeconds - (vDays * 86400) - (vHours * 3600)) // 60
    vSecs = vSeconds - (vDays * 86400) - (vHours * 3600) - (vMins * 60)

    vTimeStr = ""

    if vDays > 0:
        vTimeStr = "{0}d {1}h {2}m {3}s".format(vDays, vHours, vMins, vSecs)
    elif vHours > 0:
        vTimeStr = "{0}h {1}m {2}s".format(vHours, vMins, vSecs)
    elif vMins > 0:
        vTimeStr = "{0}m {1}s".format(vMins, vSecs)
    else:
        vTimeStr = "{0}s".format(vSecs)

    return vTimeStr



vStatus = None

try:
    vStatusFD = open(vStatusFile, 'r')
    vStatus = json.load(vStatusFD)
    vStatusFD.close()
except:
    vXymon.color = vStatusFileErrorColor
    vTraceback = "\n".join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))
    vXymon.appendMessage("Can not access status file '{0}':\n\n".format(vStatusFile))
    vXymon.appendMessage(vTraceback)


if vStatus == None:
    vXymon.updateXymon()
    sys.exit(1)


vXymon.color = XymonStatus.CLEAR

vNow = int(datetime.datetime.now().timestamp())

vTimeDiff = vNow - int(vStatus['lastUpdate'])

vDegF = (float(vStatus['sensorTempC']) * 1.8) + 32

vXymon.appendMessage('--- ESP32 Sensor Data\n\n')
vXymon.appendMessage("Temperature: {0}&degC / {1:1.1f}&degF\n".format(vStatus['sensorTempC'], vDegF))
vXymon.appendMessage("Humidity: {0}%\n".format(vStatus['humidity%']))
vXymon.appendMessage("Pressure: {0} hPa\n\n".format(vStatus['pressurehPa']))
vXymon.appendMessage("Last update: {0} ({1} ago)\n".format(vStatus['lastUpdatePretty'], PrettyTime(vTimeDiff)))

vXymon.sendData("esp32.rrd", "DS:tempC:GAUGE:600:U:U {0}\n".format(vStatus['sensorTempC']))

vXymon.updateXymon()
