import time
from PySide6.QtCore import QRunnable, QObject, Signal, QObject

# Signals
class ThreadSignals(QObject):
    FirstConnectionAttemptDone = Signal()
    OSCStatus = Signal(str)

class AcqLoop(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''
    def __init__(self, window, oscilloscope, pool):
        super().__init__()
        self.thread_signals = ThreadSignals()
        self.loop = True
        self.window = window
        self.oscilloscope = oscilloscope
        self.pool = pool
    def run_simple_acq(self):
        session_status = "IDLE"
        try:
            print("attempting connection with oscilloscope")
            self.oscilloscope.test_connection()
            session_status = "CONNECTED"
        except Exception as error:
            print("An exception occurred: ", error)
            session_status = "DISCONNECTED"
            quit()
        else:
            print("acquire samples")
            acq_samples1, acq_samples2, recording_time = self.oscilloscope.acquire_samples_single_buffer()
            self.window.update_data_graph_outputs_instrument(acq_samples1, acq_samples2, recording_time)
            self.window.update_data_graph_piezo(acq_samples1, acq_samples2, recording_time)
        finally:
            self.thread_signals.OSCStatus.emit(session_status)
            print("Finished process")
            session_status = "IDLE"
    def run_loop_acq(self):
        session_status = "NOT ESTABLISHED"
        self.loop = True
        try:
            print("attempting connection with oscilloscope")
            self.oscilloscope.test_connection()
            session_status = "CONNECTED"
        except Exception as error:
            print("An exception occurred: ", error)
            session_status = "DISCONNECTED"
        else:        
            while self.loop:
                acq_samples1, acq_samples2, recording_time = self.oscilloscope.acquire_samples_single_buffer()
                self.window.update_data_graph_outputs_instrument(acq_samples1, acq_samples2, recording_time)
                self.window.update_data_graph_piezo(acq_samples1, acq_samples2, recording_time)
                time.sleep(0.5)
        finally:
            self.thread_signals.OSCStatus.emit(session_status)
    def stop(self):
        print("stop!")
        self.loop = False # set the run condition to false on stop
    def run_acq_loop(self):
        self.pool.start(self.run_loop_acq)
    def stop_acq_loop(self):
        #worker.disconnect()
        print("you want to terminate the thread")
        self.loop = False