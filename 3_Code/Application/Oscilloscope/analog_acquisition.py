from ctypes import *
from Application import (hdwfNone, filterDecimate, DwfStateDone, DwfStateConfig, DwfStatePrefill, DwfStateArmed,
                        AnalogOutNodeCarrier, funcSine, acqmodeRecord, trigsrcDetectorAnalogIn, trigtypeEdge, 
                        DwfTriggerSlopeRise)
import time
import numpy as np

class Oscilloscope:
    def __init__(self):
        self.exceptions = ConnectionError()
        self.frequency = 0
        self.num_samples = 0
        self.trigger_source = 0
        self.trigger_level = 0
        self.voltage_range = 5
        self.dwf = cdll.dwf
        #declare ctype variables
        self.hdwf = c_int()
        self.sts = c_byte()

        self.initial_configuration_acquisition()
    def test_connection(self):
        version = create_string_buffer(16)
        self.dwf.FDwfGetVersion(version)
        #print("hdwf value is: {}".format(self.hdwf.value))
        #print("DWF Version: "+str(version.value))
        if self.hdwf.value == hdwfNone.value:
            szerr = create_string_buffer(512)
            self.dwf.FDwfGetLastErrorMsg(szerr)
            print(str(szerr.value))
            raise Exception("Digilent Discovery 2 is not connected")
        else:
            print("Device connected")

    def initial_configuration_acquisition(self):
        version = create_string_buffer(16)
        self.dwf.FDwfGetVersion(version)

        #open device
        self.dwf.FDwfDeviceOpen(c_int(-1), byref(self.hdwf))
        if self.hdwf.value == hdwfNone.value:
            szerr = create_string_buffer(512)
            self.dwf.FDwfGetLastErrorMsg(szerr)
            print(str(szerr.value))
            print("failed to open device")
    def set_frequency(self, frequency):
        frequency = c_double(float(frequency))
        self.frequency = frequency
        self.dwf.FDwfAnalogInFrequencySet(self.hdwf, frequency)
        print("Sampling rate: "+str(frequency))
    def set_num_samples(self, num_samples):
        self.num_samples = num_samples
    def set_trigger_source(self, trigger_source):
        self.trigger_source = trigger_source
    def set_trigger_level(self, trigger_level):
        self.trigger_level = trigger_level
    def set_range_set(self):
        self.num_samples = range
        self.dwf.FDwfAnalogInChannelRangeSet(self.hdwf, c_int(-1), c_double(range))
    def generate_output_testing(self):
        print("Generating sine wave...")
        self.dwf.FDwfAnalogOutNodeEnableSet(self.hdwf, c_int(0), AnalogOutNodeCarrier, c_int(1))
        self.dwf.FDwfAnalogOutNodeFunctionSet(self.hdwf, c_int(0), AnalogOutNodeCarrier, funcSine)
        self.dwf.FDwfAnalogOutNodeFrequencySet(self.hdwf, c_int(0), AnalogOutNodeCarrier, c_double(1000))
        self.dwf.FDwfAnalogOutNodeAmplitudeSet(self.hdwf, c_int(0), AnalogOutNodeCarrier, c_double(2))
        self.dwf.FDwfAnalogOutConfigure(self.hdwf, c_int(0), c_int(1))     
    def acquire_samples_single_buffer(self):
        num_samples = self.num_samples
        trigger_source = self.trigger_source
        trigger_level = self.trigger_level
        rgdSamples1 = (c_double*num_samples)()
        rgdSamples2 = (c_double*num_samples)()
        #print("Starting oscilloscope")

        #set up acquisition
        cBufMax = c_int()
        self.dwf.FDwfAnalogInBufferSizeInfo(self.hdwf, 0, byref(cBufMax))
        #print("Device buffer size: "+str(cBufMax.value))
        self.dwf.FDwfAnalogInBufferSizeSet(self.hdwf, c_int(num_samples))
        #print("Device buffer size set to: "+str(num_samples))
        self.dwf.FDwfAnalogInChannelEnableSet(self.hdwf, c_int(0), c_int(1)) #-1?
        #self.dwf.FDwfAnalogInChannelFilterSet(self.hdwf, c_int(-1), filterDecimate)

        #set up trigger
        self.dwf.FDwfAnalogInTriggerAutoTimeoutSet(self.hdwf, c_double(2)) #auto trigger in 2 seconds
        self.dwf.FDwfAnalogInTriggerSourceSet(self.hdwf, trigsrcDetectorAnalogIn) #one of the analog in channels
        self.dwf.FDwfAnalogInTriggerTypeSet(self.hdwf, trigtypeEdge)
        self.dwf.FDwfAnalogInTriggerChannelSet(self.hdwf, c_int(trigger_source)) # first channel
        self.dwf.FDwfAnalogInTriggerLevelSet(self.hdwf, c_double(trigger_level)) # 0.5V
        self.dwf.FDwfAnalogInTriggerConditionSet(self.hdwf, DwfTriggerSlopeRise)
        
        self.dwf.FDwfAnalogInConfigure(self.hdwf, c_int(1), c_int(1))
        for iTrigger in range(10):
            # new acquisition is started automatically after done state 
            while True:
                self.dwf.FDwfAnalogInStatus(self.hdwf, c_int(1), byref(self.sts))
                if self.sts.value == DwfStateDone.value :
                    break
                time.sleep(0.1)
                #print("Acquisition done")

        self.dwf.FDwfAnalogInStatusData(self.hdwf, 0, rgdSamples1, num_samples) # get channel 1 data
        self.dwf.FDwfAnalogInStatusData(self.hdwf, 1, rgdSamples2, num_samples) # get channel 2 data

        samples1 = np.fromiter(rgdSamples1, dtype=float)
        samples2 = np.fromiter(rgdSamples2, dtype=float)

        #dc = sum(rgdSamples1)/len(rgdSamples1)
        #print("Acquisition #"+str(iTrigger)+" average: "+str(dc)+"V")

        recording_time = []
        data_x = np.arange(num_samples)
        for element in data_x:
            instant_s = (element/self.frequency)
            recording_time.append(instant_s)

        return samples1, samples2, recording_time
    def acquire_samples_recording(self):
        #declare ctype variables
        frequency = self.frequency     
        nSamples = int(self.num_samples) 
        rgdSamples1 = (c_double*nSamples)()
        rgdSamples2 = (c_double*nSamples)()
        cAvailable = c_int()
        cLost = c_int()
        cCorrupted = c_int()
        fLost = 0
        fCorrupted = 0

        #self.generate_output_testing()

        #set up acquisition
        self.dwf.FDwfAnalogInChannelEnableSet(self.hdwf, c_int(0), c_int(1))
        self.dwf.FDwfAnalogInChannelRangeSet(self.hdwf, c_int(0), c_double(5))
        self.dwf.FDwfAnalogInAcquisitionModeSet(self.hdwf, acqmodeRecord)
        self.dwf.FDwfAnalogInRecordLengthSet(self.hdwf, c_double(nSamples/frequency.value)) #different method between acq modes

        #wait at least 2 seconds for the offset to stabilize
        time.sleep(2)

        print("Starting oscilloscope")
        self.dwf.FDwfAnalogInConfigure(self.hdwf, c_int(0), c_int(1))

        cSamples = 0

        while cSamples < nSamples:
            self.dwf.FDwfAnalogInStatus(self.hdwf, c_int(1), byref(self.sts))
            if cSamples == 0 and (self.sts == DwfStateConfig or self.sts == DwfStatePrefill or self.sts == DwfStateArmed) :
                # Acquisition not yet started.
                continue

            self.dwf.FDwfAnalogInStatusRecord(self.hdwf, byref(cAvailable), byref(cLost), byref(cCorrupted))
            
            cSamples += cLost.value

            if cLost.value :
                fLost = 1
            if cCorrupted.value :
                fCorrupted = 1

            if cAvailable.value==0 :
                continue

            if cSamples+cAvailable.value > nSamples :
                cAvailable = c_int(nSamples-cSamples)
            
            self.dwf.FDwfAnalogInStatusData(self.hdwf, c_int(0), byref(rgdSamples1, sizeof(c_double)*cSamples), cAvailable) # get channel 1 data
            self.dwf.FDwfAnalogInStatusData(self.hdwf, c_int(1), byref(rgdSamples2, sizeof(c_double)*cSamples), cAvailable) # get channel 2 data
            cSamples += cAvailable.value

        #self.dwf.FDwfAnalogOutReset(self.hdwf, c_int(0))
        self.dwf.FDwfDeviceCloseAll()
        print("Recording done")
        recording_time = []
        data_x = np.arange(nSamples)
        for element in data_x:
            instant_s = (element/frequency)
            recording_time.append(instant_s)

        acq_samples1 = np.fromiter(rgdSamples1, dtype = float)
        acq_samples2 = np.fromiter(rgdSamples2, dtype = float)

        return acq_samples1, acq_samples2, recording_time

if __name__ == "__main__":

    dwf = cdll.dwf

    hdwf = c_int()
    sts = c_byte()
    rgdSamples = (c_double*8192)()

    version = create_string_buffer(16)
    dwf.FDwfGetVersion(version)
    print("DWF Version: "+str(version.value))

    print("Opening first device")
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
    # 2nd configuration for Analog Discovery with 16k analog-in buffer
    #dwf.FDwfDeviceConfigOpen(c_int(-1), c_int(1), byref(hdwf)) 

    if hdwf.value == hdwfNone.value:
        szError = create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(szError);
        print("failed to open device\n"+str(szError.value))
        quit()

    #set up acquisition
    dwf.FDwfAnalogInFrequencySet(hdwf, c_double(20000000.0))
    dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(8192)) 
    dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_int(1))
    dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(5))

    #set up trigger
    dwf.FDwfAnalogInTriggerAutoTimeoutSet(hdwf, c_double(0)) #disable auto trigger
    dwf.FDwfAnalogInTriggerSourceSet(hdwf, trigsrcDetectorAnalogIn) #one of the analog in channels
    dwf.FDwfAnalogInTriggerTypeSet(hdwf, trigtypeEdge)
    dwf.FDwfAnalogInTriggerChannelSet(hdwf, c_int(0)) # first channel
    dwf.FDwfAnalogInTriggerLevelSet(hdwf, c_double(0.5)) # 0.5V
    dwf.FDwfAnalogInTriggerConditionSet(hdwf, DwfTriggerSlopeRise) 

    #or use trigger from other instruments or external trigger
    #dwf.FDwfAnalogInTriggerSourceSet(hdwf, trigsrcExternal1) 
    #dwf.FDwfAnalogInTriggerConditionSet(hdwf, DwfTriggerSlopeEither) 

    # wait at least 2 seconds with Analog Discovery for the offset to stabilize, before the first reading after device open or offset/range change
    time.sleep(2)

    print("Starting repeated acquisitions")
    dwf.FDwfAnalogInConfigure(hdwf, c_int(0), c_int(1))

    for iTrigger in range(10):
        # new acquisition is started automatically after done state 

        while True:
            dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
            if sts.value == DwfStateDone.value :
                break
            time.sleep(0.001)
        
        dwf.FDwfAnalogInStatusData(hdwf, 0, rgdSamples, 8192) # get channel 1 data
        #dwf.FDwfAnalogInStatusData(hdwf, 1, rgdSamples, 8192) # get channel 2 data
        
        dc = sum(rgdSamples)/len(rgdSamples)
        print("Acquisition #"+str(iTrigger)+" average: "+str(dc)+"V")
        
    dwf.FDwfDeviceCloseAll()

