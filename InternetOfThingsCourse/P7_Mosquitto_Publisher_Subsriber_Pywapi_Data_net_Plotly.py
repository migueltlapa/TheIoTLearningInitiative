#!/usr/bin/python
#!/usr/bin/python
#P7 Mosquitto Publisher, Subscriber, Pywapi Weather, Send Data Network, Plotly
#Miguel Tlapa Juarez
#migueltlapa@gmail.com
#May 5 2016
#Internet of Things Course 
import paho.mqtt.client as paho
import psutil
import pywapi
import signal
import sys
import time

from threading import Thread

import plotly.plotly as py
from plotly.graph_objs import Scatter, Layout, Figure

username = 'migueltlapa'
api_key = 'twqaqq7ept'
stream_token = 'inphe0kkoa'

def interruptHandler(signal, frame):
    sys.exit(0)

def on_publish(mosq, obj, msg):
    pass

def dataNetwork():
    netdata = psutil.net_io_counters()
    return netdata.packets_sent + netdata.packets_recv

def dataNetworkHandler():
    idDevice = "ThisDevice"
    mqttclient = paho.Client()
    mqttclient.on_publish = on_publish
    mqttclient.connect("test.mosquitto.org", 1883, 60)
    while True:
        packets = dataNetwork()
        message = idDevice + " " + str(packets)
        print "MQTT dataNetworkHandler " + message
        mqttclient.publish("IoT101/Network", message)
        time.sleep(1)

def on_message(mosq, obj, msg):
    print "MQTT dataMessageHandler %s %s" % (msg.topic, msg.payload)

def dataMessageHandler():
    mqttclient = paho.Client()
    mqttclient.on_message = on_message
    mqttclient.connect("test.mosquitto.org", 1883, 60)
    mqttclient.subscribe("IoT101/Message", 0)
    while mqttclient.loop() == 0:
        pass

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

if __name__ == '__main__':

    signal.signal(signal.SIGINT, interruptHandler)

    threadx = Thread(target=dataNetworkHandler)
    threadx.start()

    thready = Thread(target=dataMessageHandler)
    thready.start()

    threadz = Thread(target=dataPlotlyHandler)
    threadz.start()

    while True:
        print "Hello Internet of Things 101"
        dataWeatherHandler()
        time.sleep(5)

# End of File
