"""Signal generation interface"""
import pyvisa

class WaveGenerator:
    """
    Object including the necessary parameters from a wave generator as attributes
    and the methods to changed them with SCPI commands
    """
    def __init__(self):
        """Initialization of signal generator attributes. Attributes correspond
        to configuration features of the signal generator independent from the
        type of generated signal"""
        self.instrument_address = ""
        self.my_resource = ""
        #options are 1 and 2. Default is 1 (channel 1)
        self.channel = 1
        #options are: SIN, SQU, TRI, RAMP, PULS, PRBS, NOIS, ARB or DC. By default we choose DC
        self.function_type = "DC"
        self.frequency = 0
        self.max_voltage = 0
        self.min_voltage = 0
        self.phase = 0
        self.output = "OFF"
    def create_resource_manager(self):
        """
        Creates a resource manager object. This class contains a method that lists
        the devices that are connected to the computer.
        """
        resource_manager = pyvisa.ResourceManager() 
        self.my_resource = resource_manager.open_resource(self.instrument_address) 
    def test_connection(self):
        """Method to test connection with the device once session was opened"""
        self.my_resource.query("*IDN?")
    def set_channel(self, channel):
        """Method to set the output of the signal generator"""
        self.channel = channel
        #self.my_resource.write("SOURCE{}".format(channel))
    def set_function(self, function_type):
        """Method to set the type of signal of the signal generator"""
        self.function_type = function_type
        self.my_resource.write("SOURCE{}:FUNCTION {}".format(self.channel, function_type))
    def set_frequency(self, frequency):
        """Method to set the frequency of signal"""
        self.frequency = frequency
        self.my_resource.write("SOURCE{}:FREQUENCY {}".format(self.channel, frequency))
    def set_max_voltage(self, max_voltage):
        """Method to set the maximum voltage of the signal"""
        self.max_voltage = max_voltage
        self.my_resource.write("SOURCE{}:VOLTAGE:HIGH {}".format(self.channel, max_voltage))
    def set_min_voltage(self, min_voltage):
        """Method to set the minimum voltage of the signal"""
        self.min_voltage = min_voltage
        self.my_resource.write("SOURCE{}:VOLTAGE:LOW {}".format(self.channel, min_voltage))
    def set_phase(self, phase):
        """Method to set the phase of the signal"""
        self.phase = phase
        self.my_resource.write("SOURCE{}:PHASE {}".format(self.channel, phase))
        self.my_resource.write("PHASE:SYNC")
    def turn_output(self, output):
        """Method to turn on or off the output of the signal generator"""
        self.output = output
        self.my_resource.write("OUTPUT"+str(self.channel)+" "+str(output))

    def sine_wave(self, frequency, max_voltage, min_voltage, phase):
        """Method that takes the attributes of the class Wave Generator 
        and sets them into a sine wave with the user values"""
        #sine_generator = self.my_resource
        #set_source will set the last value set by the user. If it was not changed,
        # it will be the default value defined in the attributes of the class
        self.set_channel(self.channel)
        self.set_function(function_type="SIN")
        self.set_frequency(frequency)
        self.set_max_voltage(max_voltage)
        self.set_min_voltage(min_voltage)
        self.set_phase(phase)

if __name__ == "__main__":
    wavgen1 = WaveGenerator()
    wavgen1.instrument_address='TCPIP0::128.141.116.223::inst0::INSTR'
    try:
        # we create our instance of the class wavgen
        wavgen1.set_frequency(frequency=100)
        wavgen1.set_channel(channel=2)
        wavgen1.set_frequency(frequency=300)
        wavgen1.turn_output("OFF")
    except pyvisa.errors.VisaIOError:
        print("No connection to: " + wavgen1)
