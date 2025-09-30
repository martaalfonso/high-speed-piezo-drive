# Only needed for access to command line arguments
import sys
from PySide6.QtCore import QSize, Qt, Signal, QEvent, QObject
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QGroupBox, 
                               QLabel, QCheckBox, QPushButton, QMessageBox, QHBoxLayout, QGridLayout, QLineEdit,
                               QCompleter)
from PySide6.QtGui import QPixmap, QIcon
import numpy as np
import pyqtgraph as pg
           
# To create a custom window, subclass QMainWindow
class MainWindow(QMainWindow):
    # Signals
    addressEntered = Signal(str)
    CH1MAXvoltEntered = Signal(str)
    CH1MINvoltEntered = Signal(str)
    CH1freqEntered = Signal(str)
    CH1phaseEntered = Signal(str)
    CH2MAXvoltEntered = Signal(str)
    CH2MINvoltEntered = Signal(str)
    CH2freqEntered = Signal(str)
    CH2phaseEntered = Signal(str)
    CHStartStopRequested = Signal(bool, bool)
    SampRateEntered = Signal(str)
    NumSamplesEntered = Signal(str)
    AcqOneRunRequested = Signal(bool)
    AcqLoopRequested = Signal(bool)
    AcqStopRequested = Signal(str)
    TrigSourcEntered = Signal(str)
    TrigLevelEntered = Signal(str)
    CurrentLoad = Signal(float)
    AmplitudeLoad = Signal(float)
    CapacitiveLoad = Signal(str)
    FrequencyLoad = Signal(float)
    BridgeParameters = Signal(dict)
    LoadParameters = Signal(dict)
    LoadWarning = Signal()

    def __init__(self):
        """
        Creates the parent widget and general layout of the application.
        Calls the rest of the widgets.
        """
        super().__init__()
        # Create window
        self.setWindowTitle("High Speed Piezo Testbench")
        self.setBaseSize(QSize(1900,1000))
        # Create central widget and grid layout
        self.layout = QGridLayout()
        widget = QWidget() #parent widget
        # Set central widget
        self.setCentralWidget(widget)
        # Call the rest of the widgets
        self.add_Instrument_COM_Controls()
        self.add_CH1_Controls()
        self.add_CH2_Controls()
        self.add_Channels_Run_Controls()
        self.add_resulting_signal_info()
        self.add_acquisition_controls()
        self.add_acquisition_Run_controls()
        self.add_graph_outputs_instrument()
        self.add_graph_piezo()
        self.add_OSC_messageBox()
        self.add_LoadWarning_messageBox()
        # Set the widgets in the grid layout
        widget.setLayout(self.layout)
    def add_Instrument_COM_Controls(self):
        """
        Creates an instance of all the widgets needed for the Instrument communication controls.
        Defines an Horizontal layout for the communication controls.
        Defines the maximum size of the COM controls.
        Defines the signals connected to widgets.
        """
        # Widget instances
        self.open_button = QPushButton("Open") #child widget
        self.address_line = QLineEdit("TCPIP0::192.168.1.100::inst0::INSTR") #child widget
        self.status_label = QLabel() #child widget
        # QLineEdit settings
        self.address_line.setPlaceholderText("Input instrument address")
        items = ["TCPIP0::128.141.116.223::inst0::INSTR"]
        self.completer = QCompleter(items) #Create an autocomplete functionality with the list "items"
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.address_line.setCompleter(self.completer)
        # Layout
        address_layout = QGridLayout()
        address_layout.addWidget(self.address_line, 0, 0)
        address_layout.addWidget(self.open_button, 0, 1)
        address_layout.addWidget(self.status_label, 1, 0) #placing label below address and open button
        self.layout.addLayout(address_layout, 0, 0) #nesting buttons_layout inside layout
        self.layout.setRowStretch(0, 0)
        # Sizing
        self.address_line.setMaximumWidth(350)
        self.open_button.setMaximumWidth(50)
        self.status_label.setMaximumHeight(20)
        # Signals
        self.open_button.clicked.connect(self.send_address) #Trigger on press of the button
        self.open_button.clicked.connect(self.send_bridge_parameters)
        #self.address_line.returnPressed.connect(self.send_address) # Trigger on press Enter
    def add_Channels_Run_Controls(self):
        # Widgets instances
        self.CH1_checkbox = QCheckBox("Channel 1")
        self.CH2_checkbox = QCheckBox("Channel 2")
        self.CH1_checkbox.setCheckable(True)
        self.CH2_checkbox.setCheckable(True)
        self.CHs_start_stop = QPushButton("start")
        self.CHs_start_stop.setCheckable(True)
        # Widget initial status, before connecting to the generator
        self.CHs_start_stop.setEnabled(False)
        # Layout
        checkbox_layout = QGridLayout()
        checkbox_layout.addWidget(self.CH1_checkbox, 0, 0)
        checkbox_layout.addWidget(self.CH2_checkbox, 1, 0)
        checkbox_layout.addWidget(self.CHs_start_stop, 0, 1)
        #checkbox_layout.setStretch(0, 0)
        self.layout.addLayout(checkbox_layout, 1, 0) #nesting buttons_layout inside layout
        # Sizing
        self.CH1_checkbox.setMaximumWidth(100)
        self.CH2_checkbox.setMaximumWidth(100)
        self.CHs_start_stop.setMaximumWidth(100)
        # Signals
        self.CH1_checkbox.toggled.connect(self.send_CH_start_stop) #Trigger on press of the button
        self.CH2_checkbox.toggled.connect(self.send_CH_start_stop)  
        self.CHs_start_stop.clicked.connect(self.send_CH_start_stop)   
        self.CHs_start_stop.clicked.connect(self.send_all_CH_values)  
    def add_CH1_Controls(self):
        """
        Creates an instance of all the widgets needed for the CH1 controls.
        Defines the location of CH1 controls in the Main Window grid.
        Declares a subgrid inside the CH1 box and lays out all the controls.
        Defines the maximum size of the CH1 controls box.
        """
        # Widget instances
        self.channel1_box = QGroupBox("Channel 1 Settings") #child widget
        self.ch1_max_volt = QLineEdit("0")
        ch1_max_volt_label = QLabel("Max voltage [V]")
        self.ch1_min_volt = QLineEdit("-1.1")
        ch1_min_volt_label = QLabel("Min voltage [V]")
        self.ch1_freq = QLineEdit("5000")
        ch1_freq_label = QLabel("Frequency [Hz]")
        self.ch1_phase = QLineEdit("0")
        ch1_phase_label = QLabel("Phase [°]")
        # Widgets initial state, before connecting to the generator
        self.channel1_box.setEnabled(False)
        # Layout
        self.layout.addWidget(self.channel1_box, 2, 0)
        self.layout.setRowStretch(1, 0)
        grid_box1 = QGridLayout()
        self.channel1_box.setLayout(grid_box1)
        grid_box1.addWidget(ch1_max_volt_label, 0, 0)
        grid_box1.addWidget(self.ch1_max_volt, 1, 0)
        grid_box1.addWidget(ch1_min_volt_label, 0, 1)
        grid_box1.addWidget(self.ch1_min_volt, 1, 1)
        grid_box1.addWidget(ch1_freq_label, 2, 0)
        grid_box1.addWidget(self.ch1_freq, 3, 0)
        grid_box1.addWidget(ch1_phase_label, 2, 1)
        grid_box1.addWidget(self.ch1_phase, 3, 1)
        # Sizing
        self.channel1_box.setMaximumWidth(400)
        self.channel1_box.setMaximumHeight(200)
        # Signals
        self.ch1_max_volt.returnPressed.connect(self.send_CH1_max_volt)
        self.ch1_min_volt.returnPressed.connect(self.send_CH1_min_volt)
        self.ch1_freq.returnPressed.connect(self.send_CH1_freq)
        self.ch1_phase.returnPressed.connect(self.send_CH1_phase)
        self.ch1_max_volt.editingFinished.connect(self.send_CH1_max_volt)
        self.ch1_min_volt.editingFinished.connect(self.send_CH1_min_volt)
        self.ch1_freq.editingFinished.connect(self.send_CH1_freq)
        self.ch1_phase.editingFinished.connect(self.send_CH1_phase)
        self.ch1_max_volt.returnPressed.connect(self.send_bridge_parameters)
        self.ch1_min_volt.returnPressed.connect(self.send_bridge_parameters)
        self.ch1_freq.returnPressed.connect(self.send_bridge_parameters)
    def add_CH2_Controls(self):
        """
        Creates an instance of all the widgets needed for the CH2 controls.
        Defines the location of CH2 controls in the Main Window grid.
        Declares a subgrid inside the CH2 box and lays out all the controls.
        Defines the maximum size of the CH2 controls box.
        """
        # Widget instances
        self.channel2_box = QGroupBox("Channel 2 Settings") #child widget
        self.ch2_max_volt = QLineEdit("1.1")
        ch2_max_volt_label = QLabel("Max voltage [V]")
        self.ch2_min_volt = QLineEdit("0")
        ch2_min_volt_label = QLabel("Min voltage [V]")
        self.ch2_freq = QLineEdit("5000")
        ch2_freq_label = QLabel("Frequency [Hz]")
        self.ch2_phase = QLineEdit("180")
        ch2_phase_label = QLabel("Phase [°]")
        # Widgets initial state, before connecting to the generator
        self.channel2_box.setEnabled(False)
        # Layout
        self.layout.addWidget(self.channel2_box, 3, 0)
        self.layout.setRowStretch(1, 0)
        grid_box2 = QGridLayout()
        self.channel2_box.setLayout(grid_box2)
        grid_box2.addWidget(ch2_max_volt_label, 0, 0)
        grid_box2.addWidget(self.ch2_max_volt, 1, 0)
        grid_box2.addWidget(ch2_min_volt_label, 0, 1)
        grid_box2.addWidget(self.ch2_min_volt, 1, 1)
        grid_box2.addWidget(ch2_freq_label, 2, 0)
        grid_box2.addWidget(self.ch2_freq, 3, 0)
        grid_box2.addWidget(ch2_phase_label, 2, 1)
        grid_box2.addWidget(self.ch2_phase, 3, 1)
        # Sizing
        self.channel2_box.setMaximumWidth(400)
        self.channel2_box.setMaximumHeight(200)
        # Signals
        self.ch2_max_volt.returnPressed.connect(self.send_CH2_max_volt)
        self.ch2_min_volt.returnPressed.connect(self.send_CH2_min_volt)
        self.ch2_freq.returnPressed.connect(self.send_CH2_freq)
        self.ch2_phase.returnPressed.connect(self.send_CH2_phase)
        self.ch2_max_volt.editingFinished.connect(self.send_CH2_max_volt)
        self.ch2_min_volt.editingFinished.connect(self.send_CH2_min_volt)
        self.ch2_freq.editingFinished.connect(self.send_CH2_freq)
        self.ch2_phase.editingFinished.connect(self.send_CH2_phase)
        self.ch2_max_volt.returnPressed.connect(self.send_bridge_parameters)
        self.ch2_min_volt.returnPressed.connect(self.send_bridge_parameters)
        self.ch2_freq.returnPressed.connect(self.send_bridge_parameters)    
    def add_resulting_signal_info(self):
        # Widget instances
        signal_info_box = QGroupBox("Bridge output") #child widget
        VLoad_label = QLabel("Voltage peak load [V]")
        self.VLoad_value = QLabel("")
        frequency_label = QLabel("Frequency [Hz]")
        self.frequency_value = QLabel("")
        current_label = QLabel("Current RMS load [A]")
        self.current_value = QLabel("")
        capacitance_label = QLabel("Capacitance load [uF]")
        self.capacitance_value = QLineEdit("8")
        # Layout
        self.layout.addWidget(signal_info_box, 4, 0)
        self.layout.setRowStretch(1, 0)
        grid_box3 = QGridLayout()
        signal_info_box.setLayout(grid_box3)
        grid_box3.addWidget(VLoad_label, 0, 0)
        grid_box3.addWidget(self.VLoad_value, 1, 0)
        grid_box3.addWidget(frequency_label, 2, 0) 
        grid_box3.addWidget(self.frequency_value, 3, 0)
        grid_box3.addWidget(current_label, 0, 1)
        grid_box3.addWidget(self.current_value, 1, 1)
        grid_box3.addWidget(capacitance_label, 2, 1)
        grid_box3.addWidget(self.capacitance_value, 3, 1)
        # Sizing
        signal_info_box.setMaximumWidth(400)
        signal_info_box.setMaximumHeight(200)
        # Signals
        self.capacitance_value.returnPressed.connect(self.send_bridge_parameters)
        self.capacitance_value.returnPressed.connect(self.send_capacitor_value)
    def add_acquisition_controls(self):
        # Widget instances
        acq_box = QGroupBox("Acquisition Settings") #child widget
        self.samp_rate = QLineEdit("100000")
        samp_rate_label = QLabel("Sampling rate [Hz]")
        self.num_samples = QLineEdit("100")
        num_samp_label = QLabel("Number of samples")
        self.trigger_source = QLineEdit("CH1")
        trigger_source_label = QLabel("Trigger Source")
        self.trigger_level = QLineEdit("-0.5")
        trigger_level_label = QLabel("Trigger Level [V]")
        # QLineEdit settings
        self.num_samples.setPlaceholderText("Max. buffer size: 8192")
        self.trigger_source.setPlaceholderText("CH1, CH2")
        items = ["CH1", "CH2"]
        self.completer = QCompleter(items) #Create an autocomplete functionality with the list "items"
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.trigger_source.setCompleter(self.completer)
        # Layout
        self.layout.addWidget(acq_box, 5, 0)
        self.layout.setRowStretch(1, 0)
        grid_box4 = QGridLayout()
        acq_box.setLayout(grid_box4)
        grid_box4.addWidget(samp_rate_label, 0, 0)
        grid_box4.addWidget(self.samp_rate, 1, 0)
        grid_box4.addWidget(num_samp_label, 2, 0) 
        grid_box4.addWidget(self.num_samples, 3, 0)
        grid_box4.addWidget(trigger_source_label, 0, 1)
        grid_box4.addWidget(self.trigger_source, 1, 1)
        grid_box4.addWidget(trigger_level_label, 2, 1)
        grid_box4.addWidget(self.trigger_level, 3, 1)
        # Sizing
        acq_box.setMaximumWidth(400)
        acq_box.setMaximumHeight(200)
        # Signals
        self.samp_rate.returnPressed.connect(self.send_samp_rate)
        self.num_samples.returnPressed.connect(self.send_num_samples)
        self.trigger_source.returnPressed.connect(self.send_trigger_source)
        self.trigger_level.returnPressed.connect(self.send_trigger_source)
        self.samp_rate.editingFinished.connect(self.send_samp_rate)
        self.num_samples.editingFinished.connect(self.send_num_samples)
        self.trigger_source.editingFinished.connect(self.send_trigger_source)
        self.trigger_level.editingFinished.connect(self.send_trigger_level)
    def add_acquisition_Run_controls(self):
        # Widgets
        self.Acq_one_run_button = QPushButton("One run")
        self.Acq_loop_button = QPushButton("Loop")
        self.Acq_abort_button = QPushButton("Stop")
        # Layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.Acq_one_run_button)
        buttons_layout.addWidget(self.Acq_loop_button)
        buttons_layout.addWidget(self.Acq_abort_button)
        self.layout.setRowStretch(6, 0)
        #self.layout.setRowStretch(6, 0)
        self.layout.addLayout(buttons_layout, 6, 0) #nesting buttons_layout inside layout
        # Sizing
        self.Acq_one_run_button.setMaximumWidth(100)
        self.Acq_loop_button.setMaximumWidth(100)
        self.Acq_abort_button.setMaximumWidth(100)
        # Signals
        self.Acq_one_run_button.clicked.connect(self.send_all_acq_values)
        self.Acq_loop_button.clicked.connect(self.send_all_acq_values)
        self.Acq_one_run_button.clicked.connect(self.send_acq_one_run) #Trigger on press of the button 
        self.Acq_loop_button.clicked.connect(self.send_acq_loop)       
        self.Acq_abort_button.clicked.connect(self.send_acq_abort)
    def add_OSC_messageBox(self):
        #Widgets
        self.OSCmessage = QMessageBox()
        self.OSCmessage.setWindowTitle("Warning!")
        self.OSCmessage.setText("Digilent Discovery 2 is not connected!")
        self.OSCmessage.setIcon(QMessageBox.Warning)
    def add_LoadWarning_messageBox(self):
        #Widgets
        self.LoadWarningMessage = QMessageBox()
        self.LoadWarningMessage.setWindowTitle("Warning!")
        self.LoadWarningMessage.setText("These channel settings could damage the amplifiers.")
        self.LoadWarningMessage.setInformativeText("Current RMS [A] requested is reaching the limits of nominal DC output values.")
        self.LoadSOAMessage = QMessageBox()
        self.LoadSOAMessage.setIconPixmap(QPixmap("3_Code\Application\GUI\images\SOA.png"))
    def add_graph_outputs_instrument(self):
        # Widgets instances
        self.graphWidget = pg.PlotWidget()
        # Layout
        self.layout.addWidget(self.graphWidget, 0, 1, 6, 1)  # Add the graph to the top-left corner, spanning 4 rows and 4 columns
        self.layout.setColumnStretch(1,2)
        # Initialize the data for the graph
        self.data_x = np.arange(100)  # Example: 100 data points
        self.data_y = np.zeros(100)  # Example: Random values
        self.data_y2 = np.zeros(100)  # Example: Random values
        # Create a plot curve
        self.graphWidget.plotItem.setMouseEnabled(y=False) #allow zoom only in X axis
        self.graphWidget.setLabel(axis="bottom", text="Time", units="seconds")
        self.graphWidget.setLabel(axis="left", text="Amplitude", units="V")
        self.graphWidget.showGrid(x = True, y= True)
        legend = self.graphWidget.addLegend()
        legend.setBrush('k')
        self.curve1 = self.graphWidget.plot(self.data_x, self.data_y, pen='y', name="Channel 1")
        self.curve2 = self.graphWidget.plot(self.data_x, self.data_y, pen='g', name="Channel 2")
    def add_graph_piezo(self):
        # Widgets instances
        self.graphWidget2 = pg.PlotWidget()
        # Layout
        self.layout.addWidget(self.graphWidget2, 0, 2, 6, 2)  # Add the graph to the top-left corner, spanning 4 rows and 4 columns
        self.layout.setColumnStretch(2,2)        
        # Initialize the data for the graph
        self.data_x = np.arange(100)  # Example: 100 data points
        self.data_y3 = np.zeros(100)  # Example: Random values
        # Create a plot curve
        self.graphWidget2.plotItem.setMouseEnabled(y=False) #allow zoom only in X axis
        self.graphWidget2.setLabel(axis="bottom", text="Time", units="seconds")
        self.graphWidget2.setLabel(axis="left", text="Amplitude", units="V")
        self.graphWidget2.showGrid(x = True, y= True)
        legend = self.graphWidget2.addLegend()
        legend.setBrush('k')  
        self.curve3 = self.graphWidget2.plot(self.data_x, self.data_y3, pen='y', name="Bridge output")
    """
    The following functions are custom slots of the widgets, which emit
    the necessary signals, received by the slots in main.py.
    """
    def send_address(self):
        address_input = self.address_line.text()
        self.addressEntered.emit(address_input) # Emit the instrument address via the addressEntered signal
    def send_CH1_max_volt(self):
        CH1_max_volt_input = self.ch1_max_volt.text()
        self.CH1MAXvoltEntered.emit(CH1_max_volt_input)
        print(CH1_max_volt_input)
    def send_CH1_min_volt(self):
        CH1_min_volt_input = self.ch1_min_volt.text()
        self.CH1MINvoltEntered.emit(CH1_min_volt_input)
        print(CH1_min_volt_input)
    def send_CH1_freq(self):
        frequency_input = self.ch1_freq.text()
        self.CH1freqEntered.emit(frequency_input)
        print(frequency_input)
    def send_CH1_phase(self):
        phase_input = self.ch1_phase.text()
        self.CH1phaseEntered.emit(phase_input)    
    def send_CH_start_stop(self):
        start_stop = self.CHs_start_stop.isChecked()
        CH1_status = self.CH1_checkbox.isChecked()
        CH2_status = self.CH2_checkbox.isChecked()
        if start_stop and ((CH1_status or CH2_status) or (CH1_status and CH2_status)): #if start was pressed and all checkboxes are checked
            self.CHs_start_stop.setText("stop")
        elif CH1_status == True and CH2_status == True and start_stop == False:
            self.CHs_start_stop.setText("start")
        elif CH1_status == False and CH2_status == False and start_stop == True:
            self.CHs_start_stop.toggle()
            self.CHs_start_stop.setText("start")
        masked_CH1_status = CH1_status and start_stop
        masked_CH2_status = CH2_status and start_stop
        self.CHStartStopRequested.emit(masked_CH1_status, masked_CH2_status)
    def send_CH2_max_volt(self):
        CH2_max_volt_input = self.ch2_max_volt.text()
        self.CH2MAXvoltEntered.emit(CH2_max_volt_input)
    def send_CH2_min_volt(self):
        CH2_min_volt_input = self.ch2_min_volt.text()
        self.CH2MINvoltEntered.emit(CH2_min_volt_input)
    def send_CH2_freq(self):
        frequency_input = self.ch2_freq.text()
        self.CH2freqEntered.emit(frequency_input)
    def send_CH2_phase(self):
        phase_input = self.ch2_phase.text()
        self.CH2phaseEntered.emit(phase_input)   
    def send_capacitor_value(self):
        capacitance_value = self.capacitance_value.text()
        self.CapacitiveLoad.emit(capacitance_value)
    def send_samp_rate(self):
        sampling_rate = self.samp_rate.text()
        self.SampRateEntered.emit(sampling_rate)
    def send_num_samples(self):
        number_samples = self.num_samples.text()
        self.NumSamplesEntered.emit(number_samples)  
    def send_trigger_source(self):
        trigger_source = self.trigger_source.text()
        self.TrigSourcEntered.emit(trigger_source)
    def send_trigger_level(self):
        trigger_level = self.trigger_level.text()
        self.TrigLevelEntered.emit(trigger_level)              
    def send_all_CH_values(self):
        self.send_CH1_max_volt()
        self.send_CH1_min_volt()
        self.send_CH1_freq()
        self.send_CH1_phase()
        self.send_CH2_max_volt()
        self.send_CH2_min_volt()
        self.send_CH2_freq()
        self.send_CH2_phase()
    def send_bridge_parameters(self):
        bridge_parameters = {
            "CH1maxvolt": self.ch1_max_volt.text(),
            "CH1minvolt": self.ch1_min_volt.text(),
            "CH2maxvolt": self.ch2_max_volt.text(),
            "CH2minvolt": self.ch2_min_volt.text(),
            "CH1freq": self.ch1_freq.text(),
            "CH2freq": self.ch2_freq.text(),
            "CLoad": self.capacitance_value.text()
        }
        self.BridgeParameters.emit(bridge_parameters)
    def send_all_acq_values(self):
        self.send_samp_rate()
        self.send_num_samples()
        self.send_trigger_source()
        self.send_trigger_level()
    def send_acq_one_run(self):
        start_request = True
        self.AcqOneRunRequested.emit(start_request) # Emit the start request
    def send_acq_loop(self):
        start_request = True
        self.send_all_acq_values()
        self.AcqLoopRequested.emit(start_request)    
    def send_acq_abort(self):
        start_request = False
        self.AcqStopRequested.emit(start_request) # Emit the start request             
    """
    Functions to update data in the window
    """
    def updateLoadParameters(self, bridge_parameters):
        self.VLoad_value.setText(bridge_parameters["VPeakLoad"])
        self.frequency_value.setText(bridge_parameters["Frequency"])
        self.current_value.setText(bridge_parameters["IRMSLoad"])
    def updateStatus(self, isSessionOpened):
        if isSessionOpened == "ESTABLISHED" or isSessionOpened == "UP":
            self.status_label.setStyleSheet("background-color: lightgreen")
            self.status_label.setText("Session opened")
            self.channel1_box.setEnabled(True)
            self.channel2_box.setEnabled(True)
            self.CHs_start_stop.setEnabled(True)
        elif isSessionOpened == "DOWN":
            self.status_label.setStyleSheet("background-color: red")
            self.status_label.setText("VISA IO Error: session was lost")
            self.channel1_box.setEnabled(False)
            self.channel2_box.setEnabled(False)
            self.CHs_start_stop.setEnabled(False)
        elif isSessionOpened == "NOT ESTABLISHED":
            self.status_label.setStyleSheet("background-color: red")
            self.status_label.setText("VISA IO Error: session did not open")
            self.channel1_box.setEnabled(False)
            self.channel2_box.setEnabled(False)
            self.CHs_start_stop.setEnabled(False)
    def updateOSCStatus(self, OSCStatus):
        print("OSCStatus: {}".format(OSCStatus))
        if OSCStatus == "CONNECTED":
            pass
        elif OSCStatus == "DISCONNECTED":
            self.OSCmessage.exec()
    def updateLoadStatus(self):
        self.LoadWarningMessage.exec()
        self.LoadSOAMessage.exec()
    def update_data_graph_outputs_instrument(self, samples1, samples2, recording_time):
        self.data_x = recording_time  # Example: 100 data points
        self.curve1.setData(self.data_x, samples1)  # Update the graph
        self.curve2.setData(self.data_x, samples2)  # Update the graph
    def update_data_graph_piezo(self, samples1, samples2, recording_time):
        self.data_x = recording_time
        samples1 = samples1*10
        samples2 = samples2*10
        piezo_estimation = samples1 - samples2
        self.curve3.setData(self.data_x, piezo_estimation)
     
if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_window = MainWindow()
    my_window.show()
    # Create an instance of QtWidget, which will be our window.
    sys.exit(app.exec())