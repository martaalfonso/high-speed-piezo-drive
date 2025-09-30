Tags: #highspeedpiezo , #piezotransducerdriver, #driver, #highspeedpiezo, #piezo

> The idea of this project is **to setup a system to generate vibrations by using an amplifier that is capable of handling high currents**. The amplifier is to be later setup as a full stand-alone system that can be used for vibration studies using preloaded piezo actuators.

This project should result in following points:

-   A stand-alone chassis using this amplifier. Review of schematics and requirements.
-   Code for generating vibrations using python or Labview. An API is a must and GUI is a plus.
- Validation of the high-speed amplifier by electrical (voltage/current) and mechanical (e.g. LDV/Optical) measurements.

The general documentation of this project is located at "G:\Departments\EN\Groups\SMM\ATB\LP\Equipment Controls\Piezo Drive Project\02_Hardware\High_speed_piezo."

As an insight: the previous power amplifier I worked with is not suitable for this kind of application since it can't source more than 300 mA.

## Meeting with Santi 26/05/23

First step should be seeing if both amplifiers work separately, using a function generator for the input and measuring amplitude and frequency of the output. Maybe I can use my previous project to test this/create an initial report.

**Don't forget to use the ventilation since the amplifiers can get really hot!**

Then I should try with a load. It can be a capacitor or a piezo stack directly. Before testing, check the ratings of the amplifier. Be careful with the amplitude you set, you should be aware of the capacitance/impedance of the load in order to not demand an excessive amount of current:

Probably the next step is to try the bridge configuration. I'm not sure if it would make sense to try it without load first:

![[PDFXEdit_jMWQn4tbXe.png]]

On the software side, I should provide an API for the function generator. One of the available function generators is one of the 33600A series from Keysight Technologies. It offers the communicate over the protocol VXI-11, a remote procedure call (RPC) protocol with TCP as its transport protocol. It could also be interesting to remotely control one of the delta elektronica PSUs if they have the RS232 controller

As the last thing to do, we should think of a casing/chassis for the amplifiers so we can use the bridge configuration as an standalone device, with interface for the following connections:

![[POWERPNT_HgB0E7WQfw.png]]

This is the setup I should implement:

![[Obsidian_zhhta5aDC6.png]]

# Meeting with Santi 29/06/23

Using the ![[HIGH_SPEED_PIEZO_DRIVER.potx.pptx]] presentation as support.

From the following topics:
- Overview of the architecture of the system
- Requirements of the system
- Electrical design
- Software design
	- API
	- GUI
- Mechanical design
- Measurements
- System validation
- Troubleshooting

we discussed the following:

## Electrical design: 
- The proposed (in the report) power supply range for each opamp in the bridge configuration is from +85 V to -20 V. This is higher than the absolute maximum rating in the datasheet of the amplifier. Should we leave it like that?
- Santi: not all the piezo stacks need to be driven at the maximum voltage, so it wont be in a lot of cases where we actually need that voltage range.

## Software design
### API
- The approach is to use PyVISA to provide a set of functions that enable to configure the signal generator to achieve the desired input signals for the amplifiers.
- Santi: on top of that, it would be nice to have a layer that manages already the phase of the signal, positive or negative amplitude and the output of the generator based on which signal you are referring to: the input of one amplifier, or the input for the other one. Then you dont need to think how to set each value. You just ask for one signal with those characteristics, and then the two actual signals are managed by the software.
### GUI
- What do we need to display in terms of measurements?
- Santi: electric measurements that help us to tell if we are generating the inputting signals we expect. This means:
	- Voltages of the outputs of the signal generator. We can measure that with the Analog Discovery 2 ADC
	- An estimation of the voltage at the output of the bridge, so taking the previous measurements and calculating the expected output at the bridge (not making the actual measurement).
	- Other measurements, such as oscilloscope measurements or the mechanical measurements, dont need to be displayed in the GUI.
	- Python is okay. Windows forms is difficult to maintain.
# Measurements
- I dont understand the "mechanical" drawings we did. I just know we have to measure with an LDV the displacement, (and then we should extract amplification and frequency?)
- Amplification and frequency




