from collections import defaultdict
from websocket import create_connection
import json 
import csv
import time
import os
import datetime
from utils import *
import math
class DataRecord:

    def __init__(self):
        self.ref_lat = 40.777888
        self.ref_lon = -79.949864
        self.airport = "KBTP"
        self.ws = create_connection("ws://192.168.10.1/traffic",1)
        self.data = defaultdict(lambda: defaultdict())
        self.filepath = '/media/storage/vid/' + datetime.date.today().strftime("%m-%d-%y") + "_adsb"

        #self.filepath = '/home/jay/AITF/adsb_recorder/' + datetime.date.today().strftime("%m-%d-%y") + "_adsb"
        self.ID_in_range = []
        self.traffic_filename = getNextFilePath(self.filepath,'.csv')
        print(self.traffic_filename)
        self.csvfile =  open(self.traffic_filename + '.csv' ,'w')
        fields =  ['ID', 'Time', 'Date', 'Altitude', 'Speed', 'Heading', 'Lat', 'Lon','Age','Range','Bearing','Tail','AltisGNSS']
        self.writer = csv.DictWriter(self.csvfile, fieldnames = fields)
        self.writer.writeheader()
        self.metar_filename = getNextFilePath(self.filepath,'.metar')
        self.write_metar = True
        print("Init")
        self.count = 0

    def getADSB(self):
        self.count = 0
        t_end = time.time() + 1
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
                    self.data[id]["AltisGNSS"] = d["AltIsGNSS"]
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
        #print(self.count)
        return True   

    def startWriting(self):
        for ID in self.ID_in_range:
            self.writer.writerow(self.data[ID])
        
        # if (self.write_metar):
        #     self.tt_end = time.time()+600 
        #     self.write_metar = False
        #     with open(self.metar_filename + '.metar' ,'a') as f:
        #         f.write(get_METAR(self.airport))
        # else:
        #     if (time.time()> self.tt_end):
        #         self.write_metar = True

       
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
                self.ID_in_range.append(ID)    


if __name__ == "__main__":

    DataInstance = DataRecord()
    while(True):
            DataInstance.getADSB()
            DataInstance.CheckData()
            DataInstance.startWriting()
