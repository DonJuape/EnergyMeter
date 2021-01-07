# Energy Meter
## Introduction
This document describes how to read out and record, with a Raspberry Pi, the energy consumption measured with an energy meter.
In my case the Energy Meter is connected to my heat pump system. I am interested in the daily energy consumption and the energy consumption profile during the day of this system.
## Hardware Setup
The energy meter I used is an ABB C11 ([ABB C11 User Manual](https://library.e.abb.com/public/f1db7577ce344f97ac2c5621cc8fd74d/2CMC486001M0201_B_en_C11_User_Manual.pdf?x-sign=pVu7AdCVZvHS0SL9Slxg1xL5eX+0l8oJIaBao391Itg4Frj+EhCpW/bs/t/biX5h)). This meter has an pulse output and the pulse frequency is a measure for the energy consumption. Basically the S0 pulse output of the energy meter works as follows. For every Wh consumed, the energy meter closes the switch between pin 20 and 21 for a duration of 100 ms. For installing the ABB C11 energy meter (or any other energy meter) to your 230 V electrical installation, please follow the installation instructions included with the meter.\
Now we need to count the pulses and we will do that with a Raspberry Pi, I used a Raspberry Pi 3B+. In below schematic it is shown how to connect the energy meter to the Pi. Note that there are two resistors in the schematic and these are needed for the following reasons. This pulls the input pin on the Raspberry Pi to ground when there is no pulse and it reduces the voltage on the input pin to below 3.3 V when there is a pulse. The latter is needed because the ABB C11 energy meter expects a voltage of min. 5 V and the voltage on the input pin of the Pi should not be higher than 3.3 V. 

![](schematic.svg)

## Script and Database
For the script I used Python 3 and I used REDIS as a database to store the energy consumption data for later analysis. The reason I used REDIS is because it is fast and reliable and I do not have to worry about data loss.\
It is important that we do not miss any pulses and therefore I used the *Button* class from the Python *gpiozero* module. With the *Button* class function *when_pressed* we will "monitor" the GPIO 20 input pin. This function will return TRUE when the meter switch between pin 20 and 21 is closed (i.e "a pulse").\
The rest of the script deals with periodically storing the date, time and associated energy consumption (and power) in the database (stored as a JSON string to facilitate easy data analysis). The script also checks if a new day has started and stores the date and energy consumption for that day in a seperate database key. Finally, we also check if the script was restarted (e.g. because of a power loss or maintenance) and if this was the case, that database entry is flagged. This way we can spot possible incomplete energy data in our later analysis.
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