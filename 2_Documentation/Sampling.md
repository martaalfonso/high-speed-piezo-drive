To sample signals correctly up to 500 kHz using an ADC with a sampling rate of 100 MS/s (Mega-Samples per second) and a buffer size of 8000 samples per channel, you need to consider a few key points:

1. **Nyquist Theorem:** The Nyquist theorem states that to accurately capture a signal without distortion, the sampling frequency must be at least twice the highest frequency component in the signal. In your case, to sample signals up to 500 kHz, the sampling frequency should be at least 1 MHz (2 * 500 kHz).

2. **Signal Bandwidth:** The ADC's effective bandwidth may be less than the sampling rate due to anti-aliasing filters and other factors. Ensure that your ADC can handle signals up to 500 kHz with minimal distortion.

3. **Anti-Aliasing Filter:** To prevent aliasing and distortion, you should apply an anti-aliasing filter to the input signal. This filter should remove frequencies above half the sampling frequency (in this case, above 50 MHz) to ensure that no high-frequency components fold back into the desired bandwidth.

4. **Buffer Size:** The buffer size of 8000 samples per channel should be sufficient for capturing signals up to 500 kHz if the sample rate is set to 1 MS/s (1 MHz). This is because the buffer can hold 8000 samples / 1 MS/s = 8 milliseconds of data, which covers the duration of a full period of a 500 kHz signal (1 / 500 kHz = 2 microseconds).

5. **Decimation or Post-Processing:** If the ADC's effective bandwidth is significantly lower than the sampling rate, you may need to decimate or post-process the acquired data to remove out-of-band noise and improve the effective resolution.

Based on the above considerations, here's a sample code outline for capturing signals up to 500 kHz with the given ADC:

```python
import time
import pydwf as dwf

def main():
    # Open the first Digilent device
    with dwf.Dwf(cleanup=True) as dwf_dev:

        # Enable Channel 1 (analog in)
        dwf_dev.analogInChannelEnableSet(0, True)

        # Set the range of Channel 1 (adjust based on your signal)
        dwf_dev.analogInChannelRangeSet(0, 5)  # 5V range

        # Set the acquisition parameters
        sample_rate = 1e6  # 1 MS/s (1 MHz)
        record_duration = 0.008  # 8 ms (8000 samples)
        buffer_size = int(sample_rate * record_duration)

        # Configure the acquisition
        dwf_dev.analogInFrequencySet(sample_rate)
        dwf_dev.analogInBufferSizeSet(buffer_size)
        dwf_dev.analogInConfigure()

        print("Starting acquisition...")
        dwf_dev.analogInStatusSet(1)
        dwf_dev.analogInStatusSet(1)

        # Wait for the acquisition to complete
        while True:
            if dwf_dev.analogInStatus(1) == dwf.STATE_DONE:
                break
            time.sleep(0.1)

        print("Acquisition completed!")

        # Get the acquired data from Channel 1
        data = dwf_dev.analogInStatusData(0, buffer_size)
        # The data variable contains the captured analog values from Channel 1.

        # Print the first 10 samples for demonstration purposes
        print("First 10 samples:")
        for i in range(10):
            print(f"Sample {i}: {data[i]} V")

if __name__ == "__main__":
    main()
```

In this code, we set the sample rate to 1 MS/s (1 MHz) and the buffer size to hold 8000 samples (equivalent to 8 ms of data). This allows us to capture signals up to 500 kHz correctly.

However, it is essential to verify that your ADC's effective bandwidth can handle signals up to 500 kHz and that the anti-aliasing filter is applied correctly to prevent aliasing. Additionally, consider other factors such as noise and resolution in your ADC and signal conditioning circuitry.