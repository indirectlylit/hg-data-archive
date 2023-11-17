'''
Devon Rueckner
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import IPython.display as dsp


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


def load(nodes, series):
    columnNames = ['ip', 'max_rate', 'rate', 'drop_rate', 'size', 'speed']
    return {
        'n'       : nodes,
        'state'   : 'stressed' if series == 'b' else 'safe',
        'table'   : pd.read_csv(
                        'no-logging/{0}{1}.csv'.format(n, series),
                        names=columnNames, skiprows=1, index_col='ip'
                    ).dropna()
    }

screenshotData = []
for n in (4, 5, 6, 7, 8):               # number of nodes
    screenshotData.append(load(n, 'a'))    # unstressed data
    screenshotData.append(load(n, 'b'))    # stressed data


def genMetrics(data):
    rate = np.average(data['table']['rate'])
    total_rate = np.sum(data['table']['rate'])
    size = np.average(data['table']['size'])

    stats = (
        data['n'],
        data['state'],
        np.average(data['table']['drop_rate']),
        np.average(data['table']['max_rate']),
        rate,
        size,
        rate * size / 1024.0,   # 1 KB = 1024 bytes
        total_rate,
        total_rate * size / 1024.0,
    )
    return stats

colNames = ['n', 'state', 'drop_rate', 'max_rate', 'rate', 'size', 'speed', 'total_rate', 'total_speed']
allMetrics = pd.DataFrame(map(genMetrics, screenshotData), columns=colNames).set_index(['n', 'state'])
stressedMetrics = allMetrics.xs('stressed', level=1)
safeMetrics = allMetrics.xs('safe', level=1)


aggregateMetrics = allMetrics.copy()
aggregateMetrics.columns = ['Drop Rate (msgs/s)', 'Sensor Throttle (msgs/s)', 'Actual Rate (msgs/s)', 'Message Size (bytes)', 'Average Sensor Speed (KB/s)', 'Cumulative Throughput (msgs/s)', 'Cumulative Throughput (KB/s)']
aggregateMetrics.index.names = ['Number of Nodes', None]
aggregateMetrics = np.round(aggregateMetrics.unstack())

messageSize = allMetrics.size.mean()
def _msgRateToSpeedKBs(rate):
    return rate * messageSize / 1024.0

def _plotRateAndSpeed(rateAxis, data, rateCols, **args):
    data[rateCols].plot(ax=rateAxis, rot=0, **args)
    speedData = _msgRateToSpeedKBs(data[rateCols])
    rateAxis.set_xlabel('Number of Nodes')
    speedAxis = rateAxis.twinx()
    speedData[rateCols].plot(ax=speedAxis, rot=0, **args)
    speedAxis.set_ylim(_msgRateToSpeedKBs(rateAxis.get_ylim()[0]), _msgRateToSpeedKBs(rateAxis.get_ylim()[1]))
    speedAxis.set_ylabel("KB per second", rotation=270)
    speedAxis.legend().set_visible(False)
    speedAxis.grid(False)
    speedAxis.set_title('')
    return speedAxis



def _plotRates(fig, axes, columns):
    _plotRateAndSpeed(axes[0], stressedMetrics, columns, title="Stressed Network", kind='bar')
    _plotRateAndSpeed(axes[1], safeMetrics, columns, title="Safe (unstressed) Network", kind='bar')

    axes[0].legend().set_visible(False)
    axes[0].set_ylabel("Messages per second")
    axes[1].legend().set_visible(False)
    axes[1].set_ylabel("Messages per second")
    for t in axes[1].get_ymajorticklabels():
        t.set_visible(True)



def plotIndividualRates():
    fig, axes = plt.subplots(nrows=1, ncols=2, sharey=True, figsize=(10, 5))
    _plotRates(fig, axes, ['max_rate', 'rate', 'drop_rate'])
    fig.subplots_adjust(wspace=0.5, bottom=.3)
    handles, labels = axes[0].get_legend_handles_labels()
    plt.figlegend(handles, ["Throttle Rate", "Actual Rate", "Drop Rate"], 'lower center')


def plotCumulativeRates():
    fig, axes = plt.subplots(nrows=1, ncols=2, sharey=True, figsize=(10, 4))
    _plotRates(fig, axes, ['total_rate'])
    fig.subplots_adjust(wspace=0.5)


def plotPredictedSpeed():
    nodes = pd.Series(range(10, 80))
    rates = nodes.apply(lambda v: safeMetrics.total_rate.mean() / v)
    predictedRates = pd.DataFrame([nodes, rates], ['nodes', 'rate']).T
    predictedRates = predictedRates.set_index('nodes')

    fig, axis = plt.subplots(figsize=(8, 4))
    _plotRateAndSpeed(axis, predictedRates, ['rate'], title="Maximum Speed of a Single Node", ylim=[0,90])
    axis.legend().set_visible(False)
    axis.set_ylabel("Messages per second")
    axis.set_xlim(0, 90)
    axis.set_xlabel("Number of Nodes on the Network")


