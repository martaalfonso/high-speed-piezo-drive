# High Speed Piezo Driver

The goal of this project is to provide a testbench for testing high speed vibrations on different kinds of piezo stacks for research purposes. At this moment, the testbench will be composed by the following parts:

## Hardware
- 2 x High speed power amplifiers in bridge configuration. Evaluation kits EK57 of the APEX MP111U amplifier.
- 2 x Power Supplies. SM 70-22 of the SM1500 Series of Delta Elektronika
- Signal generator. 33600A Series from Keysight Technologies.
- ADC. Digilent Discovery 2.
## Software
- CLI with the signal generator
- GUI with controls for the signal generator and elecrtic measurements
## Measuring system
- Interferometer
## Mechanics
- TBD

## Requirements

OS and software requirements:
- Windows(10,11)
- Python(3.11)
- IO Libraries Suite from Keysight Technologies, which includes the VISA driver and the Connection Expert, both needed (current stable version)[https://www.keysight.com/us/en/lib/software-detail/computer-software/io-libraries-suite-downloads-2175637.html]
- Keysight Connection Expert (latest stable version)
- Waveforms Software from Digilent

Necessary Python packages
- PyVISA
- Install the requirements with the following command:
```pip install -r </path/to/requirements.txt>```

## Content

- 1_References: datasheets, manuals and application notes of the different components used
- 2_Documentation: generated documentation of the project
- 3_Code: code for the software components
- 4_Simulations: circuit simulation of the amplifier configuration (if any)

## Getting started

Before being able to run any command, you need to make sure your signal generator is powered on and reachable in the network or visible for your system. If it is, you also need to know its complete address, following SCPI syntax. To do so, you can open the Keysight Connection Expert. If your device doesn't appear, press Add. Choose the type of interface, choose the correct device and press OK. Now it should appear in 'My Instruments' column. Inside the device details, you will find it's VISA Address. This is an example of VISA Address:

TCPIP0::128.141.116.223::inst0::INSTR

Once the communication between your PC and your instrument is possible, you can start using the module provided by this project. To run an example, you need to follow this scheme:

- Create your signal generator as an instance of the class WaveGenerator
- Choose the channel/output you want to configure. By default, the channel being edited is CH1.
- Arrange the parameters of the signal
- Turn the output on

```my_wave_generator = WaveGenerator()```
```pool = QThreadPool.globalInstance()``` 
```connection_manager = ConnectionManager(my_wave_generator, pool)```

```connection_manager.start_openVISA_thread(address_input='TCPIP0::128.141.116.223::inst0::INSTR') #this address corresponds to the Keysight Tech Signal Generator 33600A connected to the CERN network and physically present in the 937/R-002 lab```

```my_wave_generator.set_channel(channel=1)```

```my_wave_generator.sine_wave(frequency=1000, max_voltage=1, min_voltage=-1, phase=0)```

```my_wave_generator.turn_output(output="ON")```

You can choose to use a method that is already tailored to generate a specific kind of signal as it's done above, as well as edit each specific parameter on the fly.

```my_wave_generator.set_frequency(frequency=10)```

```my_wave_generator.set_phase(frequency=0)```

To close the opened session with the signal generator, use the following command:
```my_wave_generator.my_resource.close()```

To use the GUI, run the ```main.py``` file. Example of usage:

![GUI](https://gitlab.cern.ch/mro/mechatronics/high-speed-piezo-driver/-/blob/development/2_Documentation/GUI.png)

## Roadmap

The project is under development. For the moment, it allows to have a Python interface using the VISA API, and a GUI for the remote control of the signal generator as well as visualitzation of its outputs. 

The VISA API provides a common interface for lab devices with a computer, without having to worry about the physical interface (Ethernet, GPIB, USB...). It works using SCPI commands.

The idea for the software part of this project is to provide a command interface with the instrument as well as a GUI. The completed GUI will allow the user to generate the input signals for the testbench in a fast and easy way.

## Authors
Marta Alfonso Poza: marta.alfonso@cern.ch

## License

Specify the license here. Even better, you can add a LICENSE.md file to the repository.
