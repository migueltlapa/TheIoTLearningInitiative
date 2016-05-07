#P3_Flask_Network_Data_Send_Data_Network
import psutil
import signal
import sys
import time
from flask import Flask
from flask_restful import Api, Resource
from threading import Thread

app = Flask(__name__)
api = Api(app)

def interruptHandler(signal, frame):
    sys.exit(0)

def dataNetwork():
    netdata = psutil.net_io_counters()
    return netdata.packets_sent + netdata.packets_recv

class Network1(Resource):
    def get(self):
        data = dataNetworkHandler()
        return data

def dataNetworkHandler():
    idDevice = "IoT101Device"
    packets = dataNetwork()
    message = idDevice + " " + str(packets)
    print "dataNetworkHandler " + message
    return message

api.add_resource(Network1, '/network')

if __name__ == '__main__':

    app.run(host='0.0.0.0', debug=True)
   

    while True:
        print "Hello Internet of Things 101"
        time.sleep(5)

