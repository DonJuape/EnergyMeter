sudo redis-server /etc/redis/6379.conf #Start redis server, requires redis-server to be installed
sudo screen -dmS energy python3 ./EnergyMeter/energymeter.py #Start energymeter script as screen deamon, requires screen to be installed
sudo screen -dmS energy python3 ./Dashboard/dashboard.py #Start dashboard as screen deamon, requires screen to be installed