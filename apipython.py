"""
Controller class for the Data Collector GUI
This is the controller for the GUI that lets you connect to a base, scan via rf for sensors, and stream data from them in real time.
"""

from collections import deque

from Plotter.GenericPlot import *
from AeroPy.TrignoBase import *
from AeroPy.DataManager import *


## for serial commands
import serial
import time

arduino = serial.Serial(port='COM7', baudrate=9600, timeout=.1)
time.sleep(2) ## allow for setup of arduino
print("serial setup successful")

window_size = 20
data_window = []  # Initialize the rolling window with an empty list

clr.AddReference("System.Collections")

app.use_app('PySide6')


def write_servos(angles):
    """
    Send a command to the Arduino to move servos to the specified angles.
    Angles should be a dictionary where key is the servo number (0-4)
    and value is the angle (0-180).
    """
    command = ','.join(f'S{i}:{angles[i]}' for i in angles)
    command += '\n'  # Add newline to signal end of command
    arduino.write(bytes(command, 'utf-8'))

def open_fingers():
    open = {0: 180, 1: 180, 2: 180, 3: 180, 4: 180}
    return open

def close_fingers():
    close = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    return close

def thresh_reached():
    servo_positions = close_fingers()
    write_servos(servo_positions)

def below_thresh():
    servo_positions = open_fingers()
    write_servos(servo_positions)

def update_sma(new_value, data_window, window_size):
    data_window.append(new_value)
    if len(data_window) > window_size:
        data_window.pop(0)  # Remove the oldest value to maintain window size
    return sum(data_window) / len(data_window)




class PlottingManagement():
    def __init__(self, collect_data_window, metrics, emgplot=None):
        self.base = TrignoBase(self)
        self.collect_data_window = collect_data_window
        self.EMGplot = emgplot
        self.metrics = metrics
        self.packetCount = 0  # Number of packets received from base
        self.pauseFlag = True  # Flag to start/stop collection and plotting
        self.DataHandler = DataKernel(self.base.TrigBase)  # Data handler for receiving data from base
        self.base.DataHandler = self.DataHandler
        self.outData = [[0]]
        self.Index = None
        self.newTransform = None

        self.streamYTData = False # set to True to stream data in (T, Y) format (T = time stamp in seconds Y = sample value)

    def streaming(self):
        """This is the data processing thread"""
        self.emg_queue = deque()
        while self.pauseFlag is True:
            continue
        while self.pauseFlag is False:
            self.DataHandler.processData(self.emg_plot)
            self.updatemetrics()

    def streamingYT(self):
        """This is the data processing thread"""
        self.emg_queue = deque()
        while self.pauseFlag is True:
            continue
        while self.pauseFlag is False:
            self.DataHandler.processYTData(self.emg_plot)
            self.updatemetrics()

    def vispyPlot(self):
        """Plot Thread - Only Plotting EMG Channels"""
        while self.pauseFlag is False:
            if len(self.emg_plot) >= 2:
                incData = self.emg_plot.popleft()  # Data at time T-1
                try:
                    self.outData = list(np.asarray(incData, dtype='object')[tuple([self.base.emgChannelsIdx])])

                    dataArr = [self.emg_plot[0][i][0] for i in self.base.emgChannelsIdx]
                    dataRaw = abs(dataArr[0])
                    sma_value = update_sma(dataRaw, data_window, window_size) #filtering to prevent robot hand jitter
                    print(sma_value)
                    multiplier = 2 #gives finer therhold control
                    mult = sma_value*multiplier
                    if (mult>0.1 and mult<0.6): ## if the signal is higher than the threshold for open hand, but lower than the very high spikes seen within glitches -- close the robot hand
                        thresh_reached()
                        ## tune the values within the if statement
                    else: ## otherwise, leave the hand open
                        below_thresh()

                except IndexError:
                    print("Index Error Occurred: vispyPlot()")
                if self.base.emgChannelsIdx and self.outData[0].size > 0:
                    try:
                        self.EMGplot.plot_new_data(self.outData,
                                                   [self.emg_plot[0][i][0] for i in self.base.emgChannelsIdx])
                    except IndexError:
                        print("Index Error Occurred: vispyPlot()")

    def updatemetrics(self):
        self.metrics.framescollected.setText(str(self.DataHandler.packetCount))

    def resetmetrics(self):
        self.metrics.framescollected.setText("0")
        self.metrics.totalchannels.setText(str(self.base.channelcount))

    def threadManager(self, start_trigger, stop_trigger):
        """Handles the threads for the DataCollector gui"""
        self.emg_plot = deque()

        # Start standard data stream (only channel data, no time values)
        if not self.streamYTData:
            self.t1 = threading.Thread(target=self.streaming)
            self.t1.start()

        # Start YT data stream (with time values)
        else:
            self.t1 = threading.Thread(target=self.streamingYT)
            self.t1.start()

        if self.EMGplot:
            self.t2 = threading.Thread(target=self.vispyPlot)
            if not start_trigger:
                self.t2.start()

        if start_trigger:
            self.t3 = threading.Thread(target=self.waiting_for_start_trigger)
            self.t3.start()

        if stop_trigger:
            self.t4 = threading.Thread(target=self.waiting_for_stop_trigger)
            self.t4.start()

    def waiting_for_start_trigger(self):
        while self.base.TrigBase.IsWaitingForStartTrigger():
            continue
        self.pauseFlag = False
        if self.EMGplot:
            self.t2.start()
        print("Trigger Start - Collection Started")

    def waiting_for_stop_trigger(self):
        while self.base.TrigBase.IsWaitingForStartTrigger():
            continue
        while self.base.TrigBase.IsWaitingForStopTrigger():
            continue
        self.pauseFlag = True
        self.metrics.pipelinestatelabel.setText(self.PipelineState_Callback())
        print("Trigger Stop - Data Collection Complete")
        self.DataHandler.processData(self.emg_plot)
