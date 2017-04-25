from socket import *
import json
import time
import datetime
import thread

import pigpio
pi = pigpio.pi()

config = []
DEBUG = True

print("Reading Config")
with open('config.json', 'r') as f:
    config = json.load(f)

print("Starting UDP Server on port:"+str(config["port"]))
conn = socket(AF_INET,SOCK_DGRAM)
conn.bind(('',config["port"]))
lastUpdate = datetime.datetime.now()

def applyCommands(cmds):
    global config
    if DEBUG:
        dbg = ""
        for c in cmds:
            dbg += str(ord(c))+" "
        print dbg  
    
    pi.set_PWM_dutycycle(config["pins"]["THROTTLE"], ord(cmds[0]))
    pi.set_PWM_dutycycle(config["pins"]["YAW"],      ord(cmds[1]))
    pi.set_PWM_dutycycle(config["pins"]["PITCH"],    ord(cmds[2]))
    pi.set_PWM_dutycycle(config["pins"]["ROLL"],     ord(cmds[3]))

def timeoutThread():
    while True:
        nw = datetime.datetime.now();
        time.sleep(config["receiver_timeout"]/1000.0)

        if ((nw - lastUpdate).total_seconds()*1000) > config["receiver_timeout"]:
            applyCommands("\x00\x00\x00\x00")

thread.start_new_thread(timeoutThread,());
while True:
    try:
        commands, address = conn.recvfrom(4)
        applyCommands(commands)
        lastUpdate = datetime.datetime.now();
	#feedback
	conn.sendto(commands,address)
    except Exception as e:
        print("Broke connection to client:"+str(e))
