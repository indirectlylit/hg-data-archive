'''
Devon Rueckner
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import IPython.display as dsp

import os
import re
import dateutil.parser
import ujson



styleHTML = """
<link href='http://fonts.googleapis.com/css?family=Source+Sans+Pro' rel='stylesheet' type='text/css'>
<style>
  .rendered_html {
    font-family: 'Source Sans Pro', sans-serif;
    font-size: 16px;
  }
  div.input, div.text_cell_render, div.text_cell_input {
    width: 850px;
  }
  img {
    max-width: 750px;
  }
</style>
"""

plt.rc('font', size=12, family="Source Sans Pro")

def loadData(fname):
    """
    Returns a list of dictionaries corresponding to an input file
    """

    def _flatten(d):
        """
        Returns a dictionary which contains all keys and values of all child dictionaries
        """
        output = {}
        for k in d:
            if isinstance(d[k], dict):
                child = _flatten(d[k])
                overlap = set(d.keys()).intersection(child.keys())
                if overlap:
                    for k2 in child:
                        if k2 in overlap:
                            output[k+'-'+k2] = child[k2]
                        else:
                            output[k2] = child[k2]
                else:
                    output.update(child)
            else:
                if k in output:
                    raise Exception("'{}' is a duplicate key in {}".format(k, d))
                output[k] = d[k]
        return output

    def _cleanupData(input):
        output = _flatten(input)
        output['time'] = dateutil.parser.parse(output['time'])
        return output

    with open(fname) as f:
        df = pd.DataFrame([_cleanupData(ujson.loads(line)) for line in f])
        return df.set_index('time')


def loadFiles(dirName='./'):

    fileNamePattern = re.compile(r"^(.+?) - (.+)\.txt$")

    def _fileData(fileName):
        match = fileNamePattern.match(f)
        ret = {}
        ret['fname'] = os.path.join(dirName, fileName)
        ret['time'] = dateutil.parser.parse(match.group(1).replace("'", ':'))
        ret['label'] = match.group(2)
        return ret

    files = os.listdir(dirName)
    files = [_fileData(f) for f in files if fileNamePattern.match(f)]
    files.sort(key=lambda x: x['time'])
    return files


def selectChannel(df, chan):
    return df[df['chan'] == chan].dropna(axis=1, how='all').drop('chan', 1)

