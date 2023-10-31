from websocket import create_connection
from collections import defaultdict
from utils import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import math
import datetime
import time
import csv
import json
from getradio_sd import GetRadio

class DataRecord:

    def __init__(self):
        self.ref_lat = 40.777888
        self.ref_lon = -79.949864
        self.airport = "KBTP"
        self.ws = create_connection("ws://192.168.10.1/traffic",1)
        self.data = defaultdict(lambda: defaultdict())
        self.camera_threshold = 10 #in km
        self.data = defaultdict(lambda: defaultdict())
        self.ID_in_range =[]
        self.recording = False
        # self.filename = 1 #last video filename
        self.filepath = '/media/storage/vid/' + datetime.date.today().strftime("%m-%d-%y") + '_audio'
        self.radio = GetRadio(self.filepath)
        self.max_time = float('inf')
        self.count = 0
        self.start_time = datetime.datetime.utcnow()

    def PlotADSB(self):
        fig, ax = plt.subplots()
        # ax.scatter(0,0)
        circ = plt.Circle((0,0),self.camera_threshold,color = 'red', fill=False)
        ax.add_artist(circ)
        circ = plt.Circle((0,0),20,color = 'black', fill=False)
        ax.add_artist(circ)
        circ = plt.Circle((0,0),30,color = 'black', fill=False)
        ax.add_artist(circ)
        ax.axis('equal')
        plt.grid(True)
        plt.xlim(-100,100)
        plt.ylim(-100,100)
        for ID, d in self.data.items():
            if "Range" in d:
                x = float(d['Range'])*math.sin(math.radians(float(d['Bearing']))) 
                y = float(d['Range'])*math.cos(math.radians(float(d['Bearing']))) 
                # print(x,y)
                if "Tail" in d:
                    ax.annotate(d['Tail'],(x,y))
                if "Heading" in d:
                    m = get_arrow(float(d['Heading']))
                    ax.scatter(x,y,marker=m)
                else: 
                    ax.scatter(x,y)    
        plt.savefig("temp.png")
        plt.close()    

    def getADSB(self):
        t_end = time.time() + 1
        self.count = 0
        #print(self.ws.queueSize())
        while (time.time()<t_end):
            try:
                d = json.loads(self.ws.recv())
                #print(d)
                if d['Position_valid'] == True and d['OnGround'] == False:
                    id = d["Icao_addr"]
                    self.count = self.count + 1
                    self.data[id]["Lat"] = d["Lat"]
                    self.data[id]["Lon"] = d["Lng"]
                    self.data[id]["Altitude"] = d["Alt"]
                    r, b = get_range_and_bearing(self.ref_lat,self.ref_lon,self.data[id]["Lat"],self.data[id]["Lon"] )
                    self.data[id]["Range"] = r
                    self.data[id]["Bearing"] = b

                    if d['Speed_valid'] == True:   
                        self.data[id]["Speed"] = d["Speed"]
                        self.data[id]["Heading"] = d["Track"]

                    self.data[id]["ID"] = d["Icao_addr"]
                    self.data[id]["Time"] = d["Timestamp"].split("T")[1].split(":")    
                    self.data[id]["Date"] = d["Timestamp"].split("T")[0].split("-")     
                    self.data[id]["Tail"] = d["Tail"]
                    #self.data[id]["Age"] = d["Age"]
               
            except:
                print("No ADS-B Data")
        return True  

    def startWriting(self):
        self.filepath = '/media/storage/vid/' + datetime.date.today().strftime("%m-%d-%y") + '_audio'
        if (self.recording is False):
            self.filename = getNextFilePath(self.filepath,'.txt')
            self.csvfile =  open(self.filename + '.csv' ,'w')
            fields =  ['ID', 'Time', 'Date', 'Altitude', 'Speed', 'Heading', 'Lat', 'Lon','Age','Range','Bearing','Tail']
            self.writer = csv.DictWriter(self.csvfile, fieldnames = fields)
            self.writer.writeheader()
            self.recording = True
            self.max_time = time.time() + 15*60

            for ID in self.ID_in_range:
                self.writer.writerow(self.data[ID])
            with open(self.filename + '.txt' ,'a') as f:
                 f.write("Start Time: \n")
                 f.write(str(datetime.datetime.utcnow())+"\n")
                 self.start_time = datetime.datetime.utcnow()
                 f.write(get_METAR(self.airport))

        else:
            for ID in self.ID_in_range:
                self.writer.writerow(self.data[ID])

    def stopWriting(self):
        if (self.recording):
            self.recording = False
            self.max_time = float('inf')
            self.csvfile.close()
            with open(self.filename + '.txt' ,'a') as f:
                 f.write("End Time: \n")
                 f.write(str(datetime.datetime.utcnow())+"\n")
                 f.write("Total Time: \n")
                 f.write(str(datetime.datetime.utcnow()-self.start_time)+"\n")

    def RadioControl(self):
        if (len(self.ID_in_range)>0 and time.time()<self.max_time):

            print("Recording",self.max_time-time.time())    
            self.startWriting()
            self.radio.start_recording()

        else :

            self.stopWriting()
            self.radio.stop_recording()



    def PrintData(self):
        for ID, d in self.data.items():
            if "Range" in d:
                print(ID,d["Range"],d["Age"])


    def CheckData(self):
        self.ID_in_range = []
        for ID, d in self.data.items():
            if "Date" in d:
                date = [int(i) for i in d["Date"]]
                d["Time"][-1] = d["Time"][-1].split("Z")[0]
                time = [int(math.floor(float(i))) for i in d["Time"]]
                last = datetime.datetime(date[0],date[1],date[2],time[0],time[1],time[2])
                curr = datetime.datetime.utcnow()
                self.data[ID]["Age"] = (curr-last).total_seconds()
                if((curr-last).total_seconds()>=60):
                    print("Lost",ID)
                    del self.data[ID]
            if "Range" in d:
                if (d["Range"]<self.camera_threshold):
                    self.ID_in_range.append(ID)    

if __name__ == "__main__":

    DataInstance = DataRecord()
    while(True):

        DataInstance.getADSB()
        DataInstance.CheckData()
        DataInstance.PrintData()
        DataInstance.RadioControl()
