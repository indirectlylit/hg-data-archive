#!/usr/bin/env python

'''
author: Devon Rueckner
'''

import click
import urwid
import csv
import os
import serial
import serial.tools.list_ports
import sys
import thread
import threading
import time
import ujson
from collections import deque


"""
App global state
"""
class App:
    pass

app = App()

# shared memory and port for background thread
app.serialPort = None
app.dataBuffers = {}

# flag to indicate that app is shutting down
app.exiting = False

# store the last 5 commands as tuples of (input, output)
app.history = deque(maxlen=5)

# urwid UI
app.loop = None
app.output_widget = urwid.Text("(live data loading)")
app.input_widget = urwid.Edit("")

# lists of header and key names
app.headers = []
app.toExtract = []
app.toPrompt = []


def getPort():
    """
    Searches for a port that looks like a serial-over-usb emulator
    """
    while True:
        ports = [p[0] for p in serial.tools.list_ports.grep("usb")]
        if len(ports):
            click.echo("Setting serial port to {0}".format(ports[0]))
            try:
                return serial.Serial(ports[0], 57600, timeout=0.2)
            except serial.serialutil.SerialException, e:
                click.echo("Could not connect to serial port: {0}".format(e), err=True)
                click.echo("You may need to run with `sudo`. See --help for assistance.")
                exit()
        else:
            click.echo("No USB-based serial port found. Trying again...")
        time.sleep(2)


def getSomeData(serialPort):
    """
    Make a reasonable attempt to grab some sample data from the stream
    """
    line = ""
    for i in xrange(10):
        line = serialPort.readline().strip()
        try:
            return ujson.loads(line)
        except ValueError:
            continue
    click.echo("Could not parse output from sensor: {0}".format(line), err=True)
    exit()


def backgroundReceive():
    """
    Runs in another thread, constantly pulling the latest serial data
    """
    time.sleep(0.5) # various multithreading hacks
    while True:
        if not app:
            continue
        if not app.loop:
            continue
        if app.exiting:
            return

        # pull data
        try:
            data = ujson.loads(app.serialPort.readline())
        except ValueError:
            continue
        except serial.serialutil.SerialException, e:
            click.echo("\n\nCould not retrieve data: {0}".format(e), err=True)
            # not sure what the correct way to shut down is
            thread.interrupt_main()
            exit()

        # add it to the buffers
        for k in app.toExtract:
            app.dataBuffers[k].append(data.get(k))

        # update UI
        txt = '\n'.join(["  {:<10} {:>10.2f}".format(k, getAvgData(k)) for k in app.toExtract])
        app.output_widget.set_text(txt+'\n')
        app.loop.draw_screen()


def formatList(names):
    """
    Formats a list of values for display
    """
    names = [str(n) for n in names]
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return "{} and {}".format(names[0], names[1])
    return "{}, and {}".format(', '.join(names[0:-1]), names[-1])


def updatePrompt():
    """
    Updates the command prompt display with the history and current empty prompt
    """
    prompt = "{}: ".format(formatList(app.toPrompt))
    promptHistory = '\n'.join(["{}{}\n  {}".format(prompt, h[0], h[1]) for h in app.history])
    fullPrompt = '\n'.join((promptHistory, prompt)) if app.history else prompt
    app.input_widget.set_caption(fullPrompt)
    app.input_widget.edit_text = ""


def validateInputs(inputs):
    """
    returns an error message or None for a list of input values
    """
    if not len(inputs):
        return "Input was blank."
    if len(inputs) != len(app.toPrompt):
        return "Expecting {} numbers, separated by spaces.".format(len(app.toPrompt))
    for i in inputs:
        try:
            float(i)
        except ValueError:
            return "'{}' is not a number".format(i)
    return None


def handleInput():
    """
    Pull the current input from the user, validate it, and potentially write to file
    """
    inputText = app.input_widget.edit_text
    inputs = inputText.replace(',', ' ').split()
    err = validateInputs(inputs)
    if err:
        app.history.append((inputText, err))
    else:
        # generate an output dict from serial data and user input
        output = {}
        for h in app.headers:
            if h in app.toExtract:
                output[h] = getAvgData(h)
            else:
                output[h] = inputs[app.toPrompt.index(h)]
        # write a line to the output file
        with open(app.outputFile, 'a') as f:
            writer = csv.DictWriter(f, app.headers, delimiter='\t')
            writer.writerow(output)
        # create an entry for the history
        valsInOrder = formatList([output[h] for h in app.headers])
        app.history.append((inputText, "Saved data ({}) to file.".format(valsInOrder)))

    updatePrompt()


def getAvgData(key):
    """
    return an average of the buffered data for a given key/header
    """
    vals = app.dataBuffers[key]
    if not vals:
        return 0
    return float(sum(vals))/len(vals)


def exit(err=True):
    """
    Shut down app, doing cleanup if possible
    """
    app.exiting = True
    sys.exit(1 if err else 0)


"""
Widget with basic keyboard event handling
"""
class MainWidget(urwid.Pile):
    def keypress(self, size, key):
        """
        Intercept 'enter' events.
        Let everything else propagate down to the children.
        """
        if key == 'enter':
            handleInput()
            return None
        return super(MainWidget, self).keypress(size, key)


help = '''
This script records serial data from a sensor and user input from the terminal.

Point it at a text file with tab-separated values, containing a header row on the first line.
The header row specifies the column names, which correspond to both the data coming from the
sensor and data to be entered by the user. For example:

    python collect.py output.tsv

Any header column names in the file that match data coming from the sensor will be displayed.
Any other headers will be prompted for, and can be entered as a series of space- or
comma-separated values.

For example, a file might start with this line:

    v\tc_out\tv_measured\tc_measured

In this case, the script will monitor the serial data stream for all four values. In the case
 where `v` and `c_out` are being passed from the sensor, the script will prompt for
`v_measured` and `c_measured`.

Note that the script keeps a 20-sample buffer to smooth input from the sensors. So for example
if data is being sent at 10 messages per second, the data recorded is from a 2-second windowed
average.

If you encounter permission errors related to the serial port, you may need to run with `sudo`.
'''

@click.command(help=help)
@click.argument('out', type=click.Path(exists=False, dir_okay=False, readable=True), default="")
def cli(out):
    # check file input and show help if nothing was passed in
    app.outputFile = out
    if not app.outputFile:
        click.echo(help)
        exit()
    if not os.path.exists(app.outputFile):
        click.echo("The file '{}' does exist.\nRun with --help for assistance.".format(app.outputFile), err=True)
        exit()

    # initialize serial port
    app.serialPort = getPort()

    # initialize serial port and file info
    with open(app.outputFile) as f:
        contents = f.read()
        if not csv.Sniffer().has_header(contents):
            click.echo("'{}' does not appear to have a proper header line.\nRun with --help for assistance.".format(app.outputFile), err=True)
            exit()
        app.headers = contents.splitlines()[0].strip().split('\t')

    # write a trailing endline
    if contents[-1] != '\n':
        with open(app.outputFile, 'a') as f:
            f.write('\n')

    # figure out which of the headers are available from the data stream
    sampleData = getSomeData(app.serialPort)
    keys = sampleData.keys()
    app.toExtract = [k for k in app.headers if k in keys]
    app.toPrompt = [k for k in app.headers if k not in keys]

    # set up buffers to smooth extracted data
    for k in app.toExtract:
        app.dataBuffers[k] = deque(maxlen=20)

    # basic validation of program state
    if not len(app.toExtract):
        click.echo("Headers in '{}':\n\t{}".format(app.outputFile, ', '.join(app.headers)))
        click.echo("Keys in serial stream:\n\t{}".format(', '.join(keys)))
        click.echo("Nothing in common with the file headers.", err=True)
        click.echo("Run with --help for assistance.")
        exit()
    if not len(app.toPrompt):
        click.echo("Headers in '{}':\n\t{}".format(app.outputFile, ', '.join(app.headers)))
        click.echo("Keys in serial stream:\n\t{}".format(', '.join(keys)))
        click.echo("All file headers are found in the stream, so there is nothing to input.", err=True)
        click.echo("Run with --help for assistance.")
        exit()

    # set up the urwid app
    updatePrompt()
    fileInfo = "New data points will be appended to '{}'".format(app.outputFile)
    instruct = "Enter {} values separated by spaces and press <enter>".format(len(app.toPrompt))
    if len(app.toPrompt) == 1:
        instruct = "Enter value and press <enter>"
    instruct_widget = urwid.Text("\n{}\n{}. Press ^C to quit.\n".format(fileInfo, instruct))
    main_widget = MainWidget([
        ('pack', instruct_widget),
        ('pack', app.output_widget),
        urwid.Filler(app.input_widget, valign='top')
    ], focus_item=2)

    # start a thread for receiving serial data
    t = threading.Thread(target=backgroundReceive)
    t.daemon = True
    t.start()

    # start UI event loop
    app.loop = urwid.MainLoop(main_widget)
    app.loop.run()


if __name__ == '__main__':
    try:
        # start click-based command-line interpreter
        cli()
    except KeyboardInterrupt:
        exit(False)




