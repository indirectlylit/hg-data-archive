import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import time
from datetime import timedelta

pd.set_option('display.max_columns', 200)

CHART_WIDTH = 14

SAMPLE_PERIOD_MS = 50

def _ms_to_hr(ms):
    return ms / (1000.0 * 60 * 60)


'''
all_data - normalized data table
referenceTimestampStr - time stamp of known event in data
referenceDeltaTuple - time of known event in video
videoLengthTuple - length of video
'''
def load_data(all_data, referenceTimestampStr, referenceDeltaTuple, videoLengthTuple):

    # truncate
    referenceTimestamp = pd.to_datetime(referenceTimestampStr)
    referenceDelta = timedelta(minutes=referenceDeltaTuple[0], seconds=referenceDeltaTuple[1])
    videoLength = timedelta(minutes=videoLengthTuple[0], seconds=videoLengthTuple[1])
    start = referenceTimestamp - referenceDelta
    end = start + videoLength
    data = pd.DataFrame(all_data[start:end])

    print "START", start

    # convert bools to ints
    bool_cols = [c for c in data.columns if type(data[c].dropna()[0]) == bool]
    data.loc[:,bool_cols] = data[bool_cols].apply(pd.to_numeric)

    # create resampled, normalized MultiIndex where all data types have the same length
    groups = data.groupby(['kind', 'uid'])
    period_rule = '{}ms'.format(SAMPLE_PERIOD_MS)
    resampled = groups.resample(rule=period_rule).mean().ffill()

    # set index to number of seconds
    absolute_time = (resampled.index.levels[2] - start).total_seconds()
    resampled.index.set_levels(absolute_time, level=2, inplace=True)

    return resampled


# data parse functions
def get_cap_data(data):
    cap_data = data.ix['caps', '0000'].dropna(how='all', axis=1)
    cap_data['Power in'] = cap_data.c_in * cap_data.v
    cap_data['Power out'] = (cap_data.c_out_fwd - cap_data.c_out_rev) * cap_data.v
    cap_data['Power shunts'] = cap_data.c_shunt * cap_data.v
    cap_data['Energy out'] = cap_data['Power out'].cumsum() * _ms_to_hr(SAMPLE_PERIOD_MS)
    cap_data['Energy in'] = cap_data['Power in'].cumsum() * _ms_to_hr(SAMPLE_PERIOD_MS)
    cap_data['Energy shunts'] = cap_data['Power shunts'].cumsum() * _ms_to_hr(SAMPLE_PERIOD_MS)
    return cap_data


def get_ac_box_data(data):
    ac_box_data = data.ix['acnet', '0000'].dropna(how='all', axis=1)
    ac_box_data['AC box power out'] = ac_box_data[['c_t1', 'c_t2', 'c_t3', 'c_t4']].sum(axis=1) * ac_box_data['v_ac']
    ac_box_data['AC box energy out'] = ac_box_data['AC box power out'].cumsum() * _ms_to_hr(SAMPLE_PERIOD_MS)
    return ac_box_data


def get_inverter_data(data):
    return data.ix['inv', '0000'].dropna(how='all', axis=1)


def get_bike_data(data):
    bike_data = data.ix['bike'].dropna(how='all', axis=1)
    bike_data = pd.DataFrame(bike_data.v * bike_data.c_out).reset_index().pivot(index='time', columns='uid')
    bike_data = pd.DataFrame(bike_data.sum(axis=1), columns=['Bike power out'])
    bike_data['Bike energy out'] = bike_data['Bike power out'].cumsum() * _ms_to_hr(SAMPLE_PERIOD_MS)
    return bike_data


def get_ac_sensor_data(data):
    ac_sensor_data = data.ix['4-ac'].dropna(how='all', axis=1)
    ac_sensor_data['power'] = ac_sensor_data[['c_1', 'c_2', 'c_3', 'c_4']].sum(axis=1) * ac_sensor_data['v']
    ac_sensor_data = pd.DataFrame(ac_sensor_data['power']).reset_index().pivot(index='time', columns='uid').sum(axis=1)
    ac_sensor_data = pd.DataFrame(ac_sensor_data, columns=['AC sensor power out'])
    ac_sensor_data['AC sensor energy out'] = ac_sensor_data['AC sensor power out'].cumsum() * _ms_to_hr(SAMPLE_PERIOD_MS)
    return ac_sensor_data


'''
def get_dings(data_frame):
    dings = data_frame[data_frame.chan == 'logger.state.clap'].dropna(axis=1, how='all')
    dings['val'] = 1
    return dings
'''



def _format_plot(ax, y_label=None):
    time_axis_formatter = mpl.ticker.FuncFormatter(lambda seconds, x: time.strftime('%M:%S', time.gmtime(seconds)))
    ax.xaxis.set_major_formatter(time_axis_formatter)
    ax.set_xlabel("")

    ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(60))
    ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(6))
    ax.set_ylabel(y_label)


def plot_voltage(data):
    ax = get_ac_box_data(data).v_dc.plot(title="DC Voltage", figsize=(CHART_WIDTH, 3))
    _format_plot(ax, "Voltage (V)")


def plot_cap_power(data):
    ax = get_cap_data(data)[['Power in', 'Power out', 'Power shunts']].plot(
        alpha=0.65,
        title="Cap Box Instantaneous Power"
    )
    _format_plot(ax, "Power (W)")


def plot_total_energy(data):

    f, (ax1, ax2, ax3) = plt.subplots(3, 1)
    f.set_figheight(14)

    bike_data = get_bike_data(data)
    cap_data = get_cap_data(data)
    ac_box_data = get_ac_box_data(data)
    ac_sensor_data = get_ac_sensor_data(data)

    total_cap_output = cap_data['Energy out'] + cap_data['Energy shunts']

    energy_data = pd.concat([
        bike_data['Bike energy out'],
        cap_data['Energy in'],
        total_cap_output,
        cap_data['Energy out'],
        ac_box_data['AC box energy out'],
        ac_sensor_data['AC sensor energy out']
    ], axis=1)
    energy_data.columns = [
        'Bike output',
        'Caps input',
        'Caps output + shunts',
        'Caps output',
        'AC box output',
        'AC sensor energy out'
    ]

    energy_data.plot(ax=ax1, title="Cumulative Energy")
    _format_plot(ax1, "Energy (watt hours)")

    deficit_input = pd.DataFrame(index=cap_data.index)
    deficit_input['Bike output'] = bike_data['Bike energy out'] - bike_data['Bike energy out']
    deficit_input['Caps input'] = cap_data['Energy in'] - bike_data['Bike energy out']
    deficit_input['Caps output + Shunts'] = total_cap_output - bike_data['Bike energy out']
    deficit_input['Caps output'] = cap_data['Energy out'] - bike_data['Bike energy out']

    deficit_input.plot(ax=ax2, title="Energy Deficit Relative to Bike Output")
    _format_plot(ax2, "Energy (watt hours)")

    deficit_output = pd.DataFrame(index=cap_data.index)
    deficit_output['Caps output'] = cap_data['Energy out'] - cap_data['Energy out']
    deficit_output['AC box output'] = ac_box_data['AC box energy out'] - cap_data['Energy out']
    deficit_output['AC sensor energy out'] = ac_sensor_data['AC sensor energy out'] - cap_data['Energy out']

    deficit_output.plot(ax=ax3, title="Energy Deficit Relative to Caps Output")
    _format_plot(ax3, "Energy (watt hours)")



def plot_system_state(data):
    state = pd.concat([get_ac_box_data(data).tiers, get_inverter_data(data).soft], axis=1)[['tiers', 'soft']]
    state.columns = ['Tiers', 'Inverter']
    ax = state.plot(
        figsize=(CHART_WIDTH, 2),
        ylim=(-0.5, 5),
        title="System State"
    )
    _format_plot(ax, "Items On")

