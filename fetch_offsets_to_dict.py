#!/usr/bin/env python

import urllib.request
import re
import pathlib

page = "https://github.com/frk1/hazedumper/blob/master/csgo.cs" # hazedumper gh repo
timestamp_file = str(pathlib.Path(__file__).parent.resolve()) + r"\fetch_time\prev_fetch_time.txt"

def fetchPreviousUpdateTime():
    with open(timestamp_file, "r+") as file:
        prev_time = file.read()
        file.close()
    return prev_time    

def writeNewUpdateTime(new_time):
    with open(timestamp_file, "w") as file:
        file.write(new_time)
        file.close()

def checkForUpdateTime(current_time):   # returns true if timestamp was updated
    return True if fetchPreviousUpdateTime() < current_time else False

def fetchOffsets(debug_mode):
    if(debug_mode):
        print(("loading offsets from %s" %(page)))
    offsets = {}
    request = urllib.request.Request(page)
    response = urllib.request.urlopen(request)
    response = response.read()
    for line in response.splitlines():
        try:
            if 'timestamp' in str(line):
                val = str(line).partition('timestamp = ')
                if(checkForUpdateTime(val[2][:10])): 
                    print("New HazedDumper commit detected, fetching offsets..")
                    writeNewUpdateTime(val[2][:10]) # write new timestamp to txt file
                else: 
                    print("No new commits detected, skipping offset fetch..")
        except AttributeError:
            pass
    for line in response.splitlines():
        try:
            value = re.search('0x.+?(?=<)', str(line)).group()                 #offset value
            key = re.search('<span class="pl-en">(\w+)', str(line)).group(1)   #offset key
            offsets.update({key : value})
            if(debug_mode):
                print((f"constexpr ::std::ptrdiff_t {key} = {value};"))
        except AttributeError:
            pass
    if(debug_mode):     
        print((f"{len(offsets.keys())} offsets found!"))
    return offsets    
