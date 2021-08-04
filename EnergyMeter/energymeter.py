#!/usr/bin/python3

from gpiozero import Button # Import the Button class from the GPIO Zero library to use to detect the S0 pulse rising edge
from signal import pause
from time import monotonic, sleep
from datetime import datetime, date
from os import nice, getenv
from pymongo import MongoClient
from dotenv import load_dotenv

pulsecounter = 0 # Assign start value
start = monotonic() # Start value is the current time from a monotonic clock (i.e. a clock that cannot go backwards)
interval = 0 # Assign start value
currentday = date.today().isoformat()
restart = True

INTERVAL_MAX = 120 # Energy calculation interval length in seconds
PULSE_FREQ_METER = 1000 # Pulse "frequency" in imp/kWh for the energy meter you are using (ABB C11 in this case)

S0_pulse = Button("BOARD38", False) # Meter connected to RasPi GPIO pin38 = GPIO20. Connected with an external PD and therefore internal PU/PD = False

global client
global db
if getenv("is_docker") == "true":
    client = MongoClient(username=getenv("MONGODB_ROOT_USERNAME"), password=getenv("MONGODB_ROOT_PASSWORD"), host="mongodb")
    db = client["energymeter"]
else: # If Docker is not used
    load_dotenv("../.env") # Load .env file
    client = MongoClient(username=getenv("MONGODB_ROOT_USERNAME"), password=getenv("MONGODB_ROOT_PASSWORD"), host=getenv("MONGODB_HOST"), port=getenv("MONGODB_PORT", 27017))
    db = client[getenv("MONGODB_DATABASE_NAME", "energymeter")]
    nice(0) # Low niceness to give script high priority (not required on docker)


def new_day(): # Logic for creating an object for the start of a day
    global currentday # Make currentday available within function

    currentday = date.today().isoformat() # Update currentday

    emptyday = { # Init empty start of the day dict
        "_id": currentday,
        "energy": 0,
        "restart": restart
    }

    collection=db["HP_consumption_daily"]
    collection.insert(emptyday)

def count_pulse():
    global pulsecounter
    global start
    global interval
    global restart

    stop = monotonic()
    elapsed = stop - start
    start = monotonic()
    interval += elapsed
    pulsecounter += 1

    if interval < INTERVAL_MAX:
        pass
    else: # When more time than INTERVAL_MAX has elapsed since the previous interval, energy and power are calculated
        energy = int((1000 / PULSE_FREQ_METER) * pulsecounter) # Energy consumed in the interval in Wh
        power = 3.6 * energy / interval # Average power in the interval in kW

        datapoint = { # Create a datapoint dict with the values for the elements for the pulses recorded in the current interval
            "_id": datetime.now().replace(microsecond=0).isoformat(),
            "energy": energy,
            "power": round(power, 2),
            "restart": restart
        }

        # Insert datapoint in HP_consumption collection
        collection=db["HP_consumption"]
        collection.insert(datapoint)

        # Reset pulsecounter and interval
        pulsecounter = 0
        interval = 0
       
        if date.today().isoformat() != currentday: # If this pulse is on a different day then the previous
            new_day() # Run new day function

        collectiondaily=db["HP_consumption_daily"]

        doc = {
            "$inc": {
                "energy": energy
            }
        }
        if restart == True:
            doc["$set"] = {
                "restart": restart
            }
            restart = False

        # Update HP_consumption_daily collection for the current day _id with the incremented energy and (possibly) update restart flag
        collectiondaily.update({
            "_id": currentday
        }, doc)


       
print("Started counting!")

S0_pulse.when_pressed = count_pulse # Wait for the S0 pulse rising edge

pause() # Prevent script from exiting