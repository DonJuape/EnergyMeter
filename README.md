# Energy Meter
## Introduction
This document describes how to read out and record, with a Raspberry Pi, the energy consumption data measured with an energy meter.
In my case the Energy Meter is connected to my Heat Pump system. I am interested in the daily energy consumption and the energy consumption profile during the day of this heat pump.
## Hardware Setup
The energy meter I used is an ABB C11. This meter has a S0 pulse output corresponding to the energy consumption and we will measure this pulse with the Raspberry Pi. I used a Raspberry Pi 3B+.
For installing the ABB C11 energy meter or any other energy meter please follow the installation instructions included with the meter.
Basically the S0 pulse output of the energy meter works as follows. For every Wh consumed the energy meter closes the switch between pin 20 and 21 for a duration of 100 ms.
For connecting the energy meter to the Pi, see below schematic. Note that I used two resistors for the following reasons. It pulls the input pin on the Raspberry Pi to ground when there is no pulse and it reduces the voltage on the input pin to below 3.3 V when there is a pulse. The latter is needed because the ABB C11 energy meter expects a voltage of min. 5 V and the voltage on the input pin of the Pi should not be higher than 3.3 V. 

![](schematic.svg)

## Script and Database
For the script I used Python 3 and I used REDIS as a database to store the energy consumption data for later analysis.
The reason I used REDIS is because it is fast and reliable and I do not have to worry about data loss.
We do not want to miss any pulses and therefore I used the *Button* class from the Python *GPIOzero* module. The *Button* function *when_pressed* will monitor the GPIO input pin of the Pi closing of the energy meter switch (i.e "a pulse").
The rest of the script deals with periodically storing the date, time and associated energy consumption (and power) in the database (stored as a JSON string to facilitate easy data analysis). The script also checks if a new day has started and stores the date and energy consumption for that day in a seperate database key. Finally the scripts also checks if the script was restarted and if this was the case that database entry is flagged. This way we can spot possible incomplete energy data in our later analysis.

## Software Setup
1. Install python3 and pip3
2. Install python dependecies by running 
```sh
pip3 install -r requirements.txt
```
3. Install redis-server
```sh
sudo apt install redis-server # Debian based Linux distros
```
4. Install screen
```sh
sudo apt install screen # Debian based Linux distros
```
5. Create a .env file (or rename example.env to .env) and fill in the correct values for your database
6. Run [startenergy.sh](startenergy.sh) as sudo to start script
```sh
sudo bash ./startenergy.sh
```