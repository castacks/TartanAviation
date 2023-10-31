"""
Script that scrapes data from the IEM ASOS download service for KAGC ASOS
It retrieves the wind speed and wind direction parameters in a 15-minute window of the given UTC time
The wind parameters are averaged out over the 15-minute interval if more than one value METAR string exists in that time frame
"""
import csv
import datetime
import json
import math
import os
import sys
import time
from io import StringIO
from urllib.request import urlopen
from scipy.stats import circmean
import numpy as np
from geographiclib.geodesic import Geodesic
from utils import *

from metar import Metar

now = datetime.datetime.now()

# Number of attempts to download data
MAX_ATTEMPTS = 6
# HTTPS here can be problematic for installs that don't have Lets Encrypt CA
SERVICE = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=BTP&data=metar&tz=Etc%2FUTC&format=onlycomma&latlon=no&missing=M&trace=T&direct=no&report_type=1&report_type=2"


def download_data(uri):
    """Fetch the data from the IEM
    The IEM download service has some protections in place to keep the number
    of inbound requests in check.  This function implements an exponential
    backoff to keep individual downloads from erroring.
    Args:
      uri (string): URL to fetch
    Returns:
      string data
    """
    attempt = 0
    while attempt < MAX_ATTEMPTS:
        try:
            data = urlopen(uri, timeout=300).read().decode('utf-8')
            if data is not None and not data.startswith('ERROR'):
                return data
        except Exception as exp:
            print("download_data({}) failed with {}".format(uri, exp))
            time.sleep(5)
        attempt += 1

    print("Exhausted attempts to download, returning empty data")
    return ""


def time_in_range(a, b, x):
    if a <= b:
        return a <= x <= b
    else:
        return a <= x or x <= b


def get_wind_params(dtime):
    """Calculates the mean wind direction & speed for a given timestamp + 15 minutes

    Arguments:
        dtime {datetime} -- Python datetime Object

    Returns:
        float -- The mean air density
    """
    
    dtime = dtime + datetime.timedelta(hours=4)

    service = SERVICE

    # Set the request parameters for the day
    service += dtime.strftime('&year1=%Y&month1=%m&day1=%d')
    service += dtime.strftime('&year2=%Y&month2=%m&day2=%d&')

    # Download the data
    data = download_data(service)

    # Read the data as a CSV file
    f = StringIO(data)
    reader = csv.reader(f, delimiter=',')
    metar_data = []

    first = True
    for row in reader:
        if first:
            first = False
            continue
        # Construct the METAR Object from the data we have
        metar_data.append(Metar.Metar(row[2], month=int(
            dtime.strftime('%m')), year=int(dtime.strftime('%Y'))))

    metar_to_read = []

    # range_b = (dtime + datetime.timedelta(hours=2)).time()
    range_b = (dtime + datetime.timedelta(minutes=15)).time()
    
    wind_speed = []
    wind_directions = []

    # Read every dewpoint, temperature and pressure for every metar in the given time + 2h
    for met in metar_data:
        if time_in_range(dtime.time(), range_b, met.time.time()):
            # print(met.wind_dir)
            if met.wind_speed is not None:
                wind_speed.append(met.wind_speed.value(units="KT"))
            if met.wind_dir is not None:
                wind_directions.append(met.wind_dir.value())
            # print('Wind speed =', met.wind_speed)
            # print('Wind dir = ', met.wind_dir)
    
    # Convert wind directions from degrees to radians to perform circular mean
    wind_dir_radians = [d*math.pi/180.0 for d in wind_directions]
    # Calculate the mean of every value
    if len(wind_speed) is not 0:
    	wind_speed_avg = sum(wind_speed)/len(wind_speed)
    else:
    	wind_speed_avg = 0.0
    wind_dir_avg = circmean(wind_dir_radians)
    wind_speed_avg = wind_speed_avg*0.514444 ##knots to m/s
    # print('In degrees', wind_dir_avg * 180/math.pi)
    # print('Average wind speed and wind direction in true north: {}, {}'.format(wind_speed_avg, wind_dir_avg))
    return wind_params_runway_frame(wind_speed_avg, wind_dir_avg)

def get_runway_transform_wind():
    ##Numbers are hardcoded to KBTP
    # KBTP lat lon = [40.7791, 79.9476]
    R1 = [40.778630, -79.942803]
    R2 = [40.774548, -79.959237]
    cam_ref = [ 40.777888, -79.949864]
    runway_length = 1.45
    r1, b1 = get_range_and_bearing(cam_ref[0],cam_ref[1],R1[0],R1[1])
    x1 = r1*np.sin(np.deg2rad(b1))
    y1 = r1*np.cos(np.deg2rad(b1))
    # print(x1,y1)
    r2, b2 = get_range_and_bearing(cam_ref[0],cam_ref[1],R2[0],R2[1])
    x2 = r2*np.sin(np.deg2rad(b2))
    y2 = r2*np.cos(np.deg2rad(b2))
    # print(x2,y2)
    ang = (math.pi/2)-np.arctan2(y1-y2,x1-x2)
    # print('Ang in degrees = ',ang*180/math.pi)
    # R is the matrix that converts vectors from True North frame to Runway frame ?????
    R = np.array([[np.cos(ang),-np.sin(ang)],[np.sin(ang),np.cos(ang)]]).transpose()
    # print('R shape = ', R.shape)
    return R

def wind_params_runway_frame(wind_speed_avg, wind_dir_avg):
    rotate_by_180 = np.array([[-1,0],[0,1]]) ##flip by 180 and mirror to match
    wind_vec_true_north = np.array([wind_speed_avg*np.cos(wind_dir_avg), wind_speed_avg*np.sin(wind_dir_avg)])
    rotation_matrix = rotate_by_180@get_runway_transform_wind() # 2x2 rotation matrix: convert from true north to runway frame
    wind_dir_runway_frame = np.matmul(rotation_matrix, wind_vec_true_north)
    wind_magnitude = np.linalg.norm(wind_dir_runway_frame)
    # print('Wind magnitude in runway frame =',wind_magnitude)
    wx = wind_dir_runway_frame[0]
    wy = wind_dir_runway_frame[1]
    # print('The x and y wind components are {}, {}'.format(wx, wy))
    # print('wx None? = ', wx is None)
    # print('wy None? = ', wy is None)
    return wx, wy


if __name__ == '__main__':
    try:
        time = datetime.datetime.strptime(sys.argv[1], "%Y-%m-%d-%H:%M")
    except:
        print("Please specify a time and date in YYYY-MM-DD-HH:MM format (EDT)")
        quit(1)
    get_wind_params(time)
