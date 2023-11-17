'''
@author: Devon Rueckner
The Human Grid
All Rights Reserved
'''


# from datetime import datetime, timedelta
import numpy as np
import json
import copy
import dateutil.parser
from datetime import datetime
from matplotlib.dates import DateFormatter
from matplotlib.ticker import NullFormatter, NullLocator, MultipleLocator

minutesFmt = DateFormatter("%I:%M:%S")

BLUE = "#1f9fb2"
BROWN = "#694b3a"
RED = "#c9363c"
ORANGE = "#e86a36"
YELLOW = "#eec831"



def loadLogs(*fnames):
    data = []
    for fname in fnames:
        with open(fname) as f:
            for l in f:
                d = json.loads(l)
                d['timestamp'] = dateutil.parser.parse(d['timestamp'])
                data.append(d)
                d['offset'] = (d['timestamp'] - data[0]['timestamp']).total_seconds()
    return data



def arrayFromDictList(data, *keys):
    """
    Given a list of dict objects and some key(s),
    creates a list of just the values corresponding to the key(s).
    """
    tempList = []
    for d in data:
        val = d
        for key in keys:
            val = val[key]
        tempList.append(val)
    return np.array(tempList)



def getDataRange(data, start, stop):
    """
    Given a data array and start/stop.
     (start & stop are either datetimes or integer seconds)
    Assumes data is sorted chronologically.
    """
    r = [copy.copy(d) for d in data if d["offset"] > start and d["offset"] < stop]
    setOffsets(r)
    return r




def setOffsets(data):
    for d in data:
        d['offset'] = (d['timestamp'] - data[0]['timestamp']).total_seconds()


