import numpy as np
import matplotlib.pyplot as plt

# Given values
P_ampl = 200
C_load = 8e-6 #uF
Vp_supply = 52.5

# Define the function for V_peak
def calculate_V_peak(f):
    Vpp_load = ((8*Vp_supply/(np.sqrt(2)*0.3))-np.sqrt((8*Vp_supply/(np.sqrt(2)*0.3))**2-4*(8*P_ampl/(np.pi*0.3*f*C_load))))/2
    Vp_input = Vpp_load/40
    Ip_load = C_load * np.pi*f*Vpp_load
    bridge_values = [Vp_input,Vpp_load, Ip_load]
    return bridge_values

# Generate an array of f values
f_values = np.linspace(1000, 100000, 1000)  # Adjust the range as needed

# Calculate corresponding V_peak values
bridge_values = calculate_V_peak(f_values)

# Plotting
fig, axs = plt.subplots(1,2)
#fig.suptitle('Voltage vs frequency')
axs[0].semilogx(f_values, bridge_values[0], label = "8 uF - Voltage")
axs[0].semilogx(f_values, bridge_values[2], label = "8 uF - Current")
axs[1].semilogx(f_values, bridge_values[1], label = "8 uF - Voltage")
axs[0].legend(loc='upper right')
axs[1].legend(loc='upper right')
axs[0].set_title('Max amplitude of input voltage to one amplifier')
axs[1].set_title('Max peak to peak voltage in the load')
axs[0].set_xlabel("Frequency [Hz]")
axs[1].set_xlabel("Frequency [Hz]")
axs[0].set_ylabel("Amplitude [V]/Current [A]")
axs[1].set_ylabel("Amplitude [V]")
axs[0].grid(True, which = 'both')
axs[1].grid(True, which = 'both')
axs[0].minorticks_on()
axs[1].minorticks_on()
axs[0].annotate("0.05 V, 100kHz", (100018, 0.05))
axs[0].annotate("0.55 V, 10kHz", (10002.7, 0.548))
axs[0].annotate("1.1 V, 5kHz", (5001.17, 1.121))
axs[0].annotate("3.75 V, 1.7kHz", (1705.2, 3.756))
axs[0].annotate("7.85 V, 1kHz", (1000.45, 7.845))
axs[1].annotate("2.14 V, 100kHz", (100000, 2.1482))
axs[1].annotate("22 V, 10kHz", (10001.1, 21.91))
axs[1].annotate("45 V, 5kHz", (5001.11, 44.86))
axs[1].annotate("150 V, 1.7kHz", (1703.45, 150.1))
axs[1].annotate("313 V, 1kHz", (1004.65, 313.3))
plt.grid(True)
plt.show()

"""
plt.plot(f_values, bridge_values[1])
plt.xscale('log')
plt.xlabel('f')
plt.ylabel('Vpp_load')
plt.title('Vpp_load as a Function of f')
plt.grid(True)
plt.show()
"""