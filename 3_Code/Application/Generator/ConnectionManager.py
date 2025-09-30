import time
import pyvisa
from PySide6.QtCore import Signal, QObject

# Signals
class ThreadSignals(QObject):
    FirstConnectionAttemptDone = Signal()
    windowStatus = Signal(str)
class ConnectionManager():
    def __init__(self, generator, pool):
        self.generator = generator
        self.pool = pool
        self.thread_signals = ThreadSignals()
    def connection_watchdog(self):
        print("watchdog was started")
        while True:
            time.sleep(2)
            try:
                self.generator.test_connection()
            except pyvisa.errors.VisaIOError as error:
                print("There was an exception:", error)
                session_status = "DOWN"
            else:
                session_status = "UP"
            finally:
                #self.window.updateStatus(session_status)
                self.thread_signals.windowStatus.emit(session_status)
    def start_watchdog(self):
        self.pool.start(self.connection_watchdog)
    def open_visa_connection(self, address_input):
        session_status = "NOT ESTABLISHED"
        self.generator.instrument_address = address_input 
        try:
            print("attempting connection")
            self.generator.create_resource_manager()
            session_status = "ESTABLISHED"
            print("Session number is {}".format(str(self.generator.my_resource.session)))
        except pyvisa.errors.VisaIOError:
            session_status = "NOT ESTABLISHED"
            print("There was a VisaIOError. Session did not open")
        else:
            self.thread_signals.FirstConnectionAttemptDone.emit()
            print("Attempting to start the watchdog")
        finally:
            self.thread_signals.windowStatus.emit(session_status)
    def start_openVISA_thread(self, address_input):
        self.pool.start(self.open_visa_connection(address_input))
    def manage_closing(self):
        self.generator.set_channel(1)
        self.generator.turn_output("OFF")
        self.generator.set_channel(2)
        self.generator.turn_output("OFF")
        self.generator.my_resource.close()