from Application import MainWindow, ConnectionManager, WaveGenerator, Oscilloscope, AcqLoop
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Signal, QThreadPool
import math
import numpy as np

# Signals

# Slots
def send_start_stop(channel1_status, channel2_status):
        print("Received status are {} and {}".format(channel1_status, channel2_status))
        if channel1_status == 0 and channel2_status == 0:
            print("Sent to instrument")
            generator.set_channel(channel=1)
            generator.turn_output(output="OFF")
            generator.set_channel(channel=2)
            generator.turn_output(output="OFF")        
        elif channel1_status == 1 and channel2_status == 0:
            print("Sent to instrument")
            generator.set_channel(channel=1)
            generator.turn_output(output="ON")
            generator.set_channel(channel=2)
            generator.turn_output(output="OFF")
        elif channel1_status == 0 and channel2_status == 1:
            print("Sent to instrument")
            generator.set_channel(channel=1)
            generator.turn_output(output="OFF")
            generator.set_channel(channel=2)
            generator.turn_output(output="ON")     
        elif channel1_status == 1 and channel2_status == 1:
            print("Sent to instrument")
            generator.set_channel(channel=1)
            generator.turn_output(output="ON")
            generator.set_channel(channel=2)
            generator.turn_output(output="ON")
def send_CH1_MAX_volt(CH1maxvolt):
        generator.set_channel(channel=1)
        generator.set_max_voltage(max_voltage=CH1maxvolt)
def send_CH1_MIN_volt(CH1minvolt):
        generator.set_channel(channel=1)
        generator.set_min_voltage(min_voltage=CH1minvolt)
def send_CH1_freq(CH1freq):
        generator.set_channel(channel=1)
        generator.set_frequency(frequency=CH1freq)  
def send_CH1_phase(CH1phase):
        generator.set_channel(channel=1)
        generator.set_phase(phase=CH1phase)
def send_CH2_MAX_volt(CH2maxvolt):
        generator.set_channel(channel=2)
        generator.set_max_voltage(max_voltage=CH2maxvolt)
def send_CH2_MIN_volt(CH2minvolt):
        generator.set_channel(channel=2)
        generator.set_min_voltage(min_voltage=CH2minvolt)
def send_CH2_freq(CH2freq):
        generator.set_channel(channel=2)
        generator.set_frequency(frequency=CH2freq) 
def send_CH2_phase(CH2phase):
        generator.set_channel(channel=2)
        generator.set_phase(phase=CH2phase)
def send_samp_rate(sampling_rate):
        oscilloscope.set_frequency(float(sampling_rate)) #accepted data type by Discovery2
def send_num_samples(number_samples):
        oscilloscope.set_num_samples(int(number_samples)) #accepted data type by Discovery2
def send_trig_sourc(trigger_source):
        if trigger_source == "CH1":
            oscilloscope.set_trigger_source(0)
        elif trigger_source == "CH2":
            oscilloscope.set_trigger_source(1)
def send_trig_level(trigger_level):
        oscilloscope.set_trigger_level(float(trigger_level))
def calculate_bridge_output(bridge_parameters):
        # Given values
        P_ampl_max = 200
        C_load = 8e-6
        Vp_supply = 52.5
        CH1maxvolt = float(bridge_parameters["CH1maxvolt"])
        CH1minvolt = float(bridge_parameters["CH1minvolt"])
        CH2maxvolt = float(bridge_parameters["CH2maxvolt"])
        CH2minvolt = float(bridge_parameters["CH2minvolt"])
        CH1freq = float(bridge_parameters["CH1freq"])
        CH2freq = float(bridge_parameters["CH2freq"])
        CLoad = float(bridge_parameters["CLoad"])
        VLoad = ((CH1maxvolt-CH1minvolt)*10 + (CH2maxvolt-CH2minvolt)*10) #Amplitude of the voltage seen by the load
        if CH1freq == CH2freq:
               frequency = CH1freq
        else:
               raise Exception("Frequency in both channels needs to be the same")
        dV_dt = 2*math.pi*frequency*VLoad
        ILoad = CLoad*0.000001 * dV_dt #Current amplitude seen by the load
        Irms = ILoad/np.sqrt(2)
        load_parameters = {
                "VPeakLoad": str(VLoad),
                "Frequency": str(frequency),
                "IRMSLoad": str(round(Irms, 2)),
                "CLoad": str(CLoad)
        }
        Psupply = Vp_supply * Irms
        Pload = np.pi/4 * 0.3 * frequency * C_load * (VLoad*2)**2
        Pampl = Psupply - Pload/2
        window.LoadParameters.emit(load_parameters)
        if math.trunc(Pampl) > P_ampl_max:
               window.LoadWarning.emit()
               

if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    generator = WaveGenerator()
    oscilloscope = Oscilloscope()
    pool = QThreadPool.globalInstance()   
    connection_manager = ConnectionManager(generator, pool)
    acquisition_loop = AcqLoop(window, oscilloscope, pool) 
    # CONNECT TO SLOTS
    window.addressEntered.connect(connection_manager.start_openVISA_thread)
    window.CH1MAXvoltEntered.connect(send_CH1_MAX_volt)
    window.CH1MINvoltEntered.connect(send_CH1_MIN_volt)
    window.CH1freqEntered.connect(send_CH1_freq)
    window.CH1phaseEntered.connect(send_CH1_phase)
    window.CH2MAXvoltEntered.connect(send_CH2_MAX_volt)
    window.CH2MINvoltEntered.connect(send_CH2_MIN_volt)
    window.CH2freqEntered.connect(send_CH2_freq)
    window.CH2phaseEntered.connect(send_CH2_phase)
    window.BridgeParameters.connect(calculate_bridge_output)
    window.LoadParameters.connect(window.updateLoadParameters)
    window.LoadWarning.connect(window.updateLoadStatus)
    window.CHStartStopRequested.connect(send_start_stop)
    window.SampRateEntered.connect(send_samp_rate)
    window.NumSamplesEntered.connect(send_num_samples)
    window.TrigSourcEntered.connect(send_trig_sourc)
    window.TrigLevelEntered.connect(send_trig_level)
    window.AcqOneRunRequested.connect(acquisition_loop.run_simple_acq)
    window.AcqLoopRequested.connect(acquisition_loop.run_acq_loop)
    window.AcqStopRequested.connect(acquisition_loop.stop_acq_loop)
    acquisition_loop.thread_signals.OSCStatus.connect(window.updateOSCStatus)
    connection_manager.thread_signals.FirstConnectionAttemptDone.connect(connection_manager.start_watchdog)
    connection_manager.thread_signals.windowStatus.connect(window.updateStatus)
    # Open the main window
    window.show()
    # Handle the closing of the window
    app.aboutToQuit.connect(connection_manager.manage_closing)
    # Start GUI thread
    app.exec()