#!/usr/bin/python
#Codigo ya corre bien menos Flask
# Funciona Plotly, MQTT,FLASK,Weather,Dweet,Freeboard no funciona Watson


import paho.mqtt.client as paho
import psutil
import dweepy  # Freeboard
import pywapi
import signal
import sys
import time
import uuid
import client as mqtt
import json
import pyupm_grove as grove

from flask import Flask
from flask_restful import Api, Resource

from threading import Thread

import plotly.plotly as py
from plotly.graph_objs import Scatter, Layout, Figure
relay=grove.GroveRelay(4)
relay.off()
relay.off()
relay.off()

#########################################################################
# Flask Mdoule
app = Flask(__name__)
api = Api(app)

class Network1(Resource):
    def get(self):
        data = dataNetworkHandler_Flask()
        return data

def dataNetworkHandler_Flask():
    idDevice = GetMACAddress()
    packets = dataNetwork()
    message = idDevice + " " + str(packets)
    print "dataNetworkHandler_Flask " + message
    return message

api.add_resource(Network1, '/network')

##########################################################################
## PLotLy Credentials

username = 'migueltlapa'
api_key = 'twqaqq7ept'
stream_token = 'inphe0kkoa'
#########################################################################

def GetMACAddress():
     macAddress = hex(uuid.getnode())[2:-1]
     macAddress = format(long(macAddress, 16),'012x')
     return macAddress


def interruptHandler(signal, frame):
    sys.exit(0)

def on_publish(mosq, obj, msg):
    pass

def dataNetwork():
    netdata = psutil.net_io_counters()
    return netdata.packets_sent + netdata.packets_recv


def dataDweetHandler():   # Freeboard
    light = grove.GroveLight(0)
    data = {}
    while True:
        data['alive'] = "1"
        data['network'] = dataNetwork()
        data['light']   = light.value()
        dweepy.dweet_for('InternetOfThings101x00', data)
        time.sleep(5)


def dataNetworkHandler():
    idDevice = GetMACAddress()
    mqttclient = paho.Client()
    mqttclient.on_publish = on_publish
    mqttclient.connect("test.mosquitto.org", 1883, 60)
    while True:
        packets = dataNetwork()
        message = idDevice + " " + str(packets)
        print "MQTT dataNetworkHandler " + message
        mqttclient.publish("IoT101/"+ idDevice + "Network", message)
        time.sleep(1)

def on_message(mosq, obj, msg):
    print "MQTT dataMessageHandler %s %s" % (msg.topic, msg.payload)

def functionDataActuator(status):
    print "Data Actuator Status %s" % status
    
    if status == "0":
        relay.off()
        
    else:
        relay.on()
        


def functionDataActuatorMqttOnMessage(mosq, obj, msg):
    print "Data Sensor Mqtt Subscribe Message!"
    functionDataActuator(msg.payload)


def dataMessageHandler():
    idDevice = GetMACAddress()
    mqttclient = paho.Client()
    mqttclient.on_message = functionDataActuatorMqttOnMessage
    mqttclient.connect("test.mosquitto.org", 1883, 60)
    mqttclient.subscribe("IoT101/" + idDevice + "Message/Actuator", 0)
    while mqttclient.loop() == 0:
        pass

# def dataWeatherHandler():
#     weather = pywapi.get_weather_from_yahoo('MXJO0043', 'metric')
#     message = "Weather report in " + weather['location']['city']
#     message = message + ", Temperature " + weather['condition']['temp'] + " C"
#     message = message + ", Atmospheric Pressure " + weather['atmosphere']['pressure'] + " mbar"
#     print message

def dataWeatherHandler():
    weather = pywapi.get_weather_from_weather_com('MXJO0043', 'metric')
    message = "Weather Report in " + weather['location']['name']
    message = message + ", Temperature " + weather['current_conditions']['temperature'] + " C"
    message = message + ", Atmospheric Pressure " + weather['current_conditions']['barometer']['reading'][:-3] + " mbar"
    print message

def dataPlotly():
    return dataNetwork()



def dataPlotlyHandler():

    py.sign_in(username, api_key)

    trace1 = Scatter(
        x=[],
        y=[],
        stream=dict(
            token=stream_token,
            maxpoints=200
        )
    )

    layout = Layout(
        title='Hello Internet of Things 101 Data'
    )

    fig = Figure(data=[trace1], layout=layout)

    print py.plot(fig, filename='Hello Internet of Things 101 Plotly')

    i = 0
    stream = py.Stream(stream_token)
    stream.open()

    while True:
        stream_data = dataPlotly()
        stream.write({'x': i, 'y': stream_data})
        i += 1
        time.sleep(0.25)




# Configuration IBM Watson
    #Set the variables for connecting to the Quickstart service
organization = "quickstart"
deviceType = "iotsample-gateway"
broker = ""
topic = "iot-2/evt/status/fmt/json"
username = ""
password = ""

macAddress = GetMACAddress()
packets = dataNetwork()
#Creating the client connection
#Set clientID and broker
clientID = "d:" + organization + ":" + deviceType + ":" + macAddress
broker = organization + ".messaging.internetofthings.ibmcloud.com"

mqttc = mqtt.Client(clientID)

#Set authentication values, if connecting to registered service
if username is not "":
        mqttc.username_pw_set(username, password=password)

mqttc.connect(host=broker, port=1883, keepalive=60)
mqttc.loop_start() 



   

if __name__ == '__main__':
    

    signal.signal(signal.SIGINT, interruptHandler)

    threadx = Thread(target=dataNetworkHandler)
    threadx.start()

    thready = Thread(target=dataMessageHandler)
    thready.start()

    threadz = Thread(target=dataPlotlyHandler)
    threadz.start()

    threadw = Thread(target=dataDweetHandler)  #Freeboard
    threadw.start()

    # threadb = Thread(target=dataIbmWatson)
    # threadb.start()
    

    #app.run(host='0.0.0.0', debug=True)   ## Flask


    while mqttc.loop() == 0:
    
        cpuutilvalue = packets
       
        print cpuutilvalue

        msg = json.JSONEncoder().encode({"d":{"cpuutil":cpuutilvalue}})
        
        mqttc.publish(topic, payload=msg, qos=0, retain=False)
        print "message published"
        
        print "Hello Internet of Things 101"
        dataWeatherHandler()
        time.sleep(5)
        pass

# End of File
