# Sensor Calibration #


## Data Collection ##

We have a python script at `collect_data/collect.py` which can be used to combine data read from a sensor's serial stream with manually entered numbers.

This script can be run on any computer (host or virtual machine) that (a) has access to serial data in `/dev/tty` and (b) has Python and [pip](https://pypi.python.org/pypi/pip/) installed.

To get started, run:

```bash
cd collect_data

# first, make sure the dependencies are installed
pip install -r requirements.txt

# read over the documentation
python collect.py --help

# generally, you'll point it at an existing file like this:
python collect.py sample_data.tsv
```

If any commands give permission-related errors, try running with `sudo`.

## Linear Regression ##

The collected data comprises of:

* a set of readings from the sensors
* a corresponding set of trusted values (e.g. from multimeters)

The goal is to model the relationship between these two data sets. With a good model, we can take future sensor readings and make accurate predictions about the real values.

We use linear regression to determine the models. The matlab script used for this is `linear_regression/calibrate.m`. You can run this in either Matlab or [Octave](https://gnu.org/software/octave/).

