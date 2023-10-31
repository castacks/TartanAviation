from geographiclib.geodesic import Geodesic
from metar import Metar
import numpy as np
import os
try:
    from urllib2 import urlopen
except:
    from urllib.request import urlopen


def get_arrow(angle):

    a = np.deg2rad(angle)
    ar = np.array([[-2.5,-5],[2.5,-5],[0,5],[-2.5,-5]]).T
    rot = np.array([[np.cos(a),np.sin(a)],[-np.sin(a),np.cos(a)]])

    return np.dot(rot,ar).T

def get_range_and_bearing(lat1,lon1,lat2,lon2):

    geod = Geodesic.WGS84
    lat2 = float(lat2)
    lon2 = float(lon2)
    g = geod.Inverse(lat1,lon1,lat2,lon2)
    
    return g['s12']/1000.0, g['azi1']


def getNextFilePath(output_folder,extd):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    highest_num = 0
    for f in os.listdir(output_folder):
        if os.path.isfile(os.path.join(output_folder, f)):
            file_name = os.path.splitext(f)[0]
            # print(file_name)
            # print(file_name.split('_'))
            file_name = file_name.split('_')[0]
            ext = os.path.splitext(f)[1]
            try:
                file_num = int(file_name)
                if file_num > highest_num and ext == extd:
                    highest_num = file_num
            except ValueError:
                'The file name "%s" is not an integer. Skipping' % file_name

    output_file = os.path.join(output_folder, str(highest_num + 1))
    return output_file

def Sort_Tuple(tup):  
      
    # getting length of list of tuples 
    lst = len(tup)  
    for i in range(0, lst):  
          
        for j in range(0, lst-i-1):  
            if (tup[j][1] > tup[j + 1][1]):  
                temp = tup[j]  
                tup[j]= tup[j + 1]  
                tup[j + 1]= temp  
    return tup

def sort_list(filelist):

    mlist = []
    for i in range(len(filelist)):
        num = filelist[i]['name']
        name = int(num[1:8])
        mlist.append((filelist[i]['url'],name))
    #print(mlist)
    sorted_mlist = Sort_Tuple(mlist)
    #print(sorted_mlist)
    return sorted_mlist


def get_METAR(airport): 
    try:
        BASE_URL = "http://tgftp.nws.noaa.gov/data/observations/metar/stations"
        url = "%s/%s.TXT" % (BASE_URL, airport)
        urlh = urlopen(url)
        report = ""
        for line in urlh:
            if not isinstance(line, str):
                line = line.decode()  # convert Python3 bytes buffer to string
            if line.startswith(airport):
                report = line.strip()
                obs = Metar.Metar(line)
                return obs.string()
    except:
        return "No metar data"



