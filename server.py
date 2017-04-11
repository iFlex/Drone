from socket import *
import pigpio
import json

pi = pigpio.pi()
config = []
DEBUG = True

print("Reading Config")
with open('config.json', 'r') as f:
    config = json.load(f)

print("Starting UDP Server on port:"+str(config["port"]))
conn = socket(AF_INET,SOCK_DGRAM)
conn.bind(('',config["port"]))

def applyCommands(cmds):
    global config
    if DEBUG == True:
        dbg = ""
        for c in cmds:
            dbg += ord(c)+" "
        print dbg  
    
    pi.set_PWM_dutycycle(config["pins"]["THROTTLE"], cmds[0])
    pi.set_PWM_dutycycle(config["pins"]["YAW"],      cmds[1])
    pi.set_PWM_dutycycle(config["pins"]["PITCH"],    cmds[2])
    pi.set_PWM_dutycycle(config["pins"]["ROLL"],     cmds[3])

alive = True
def timeoutThread():
    #todo check timestamp
    while True:
        alive = False
        #sleep
        #if alive == False:
        #    applyCommands();

#threading.start_thread(timeoutThread,());
while True:
    try:
        commands, address = conn.recvfrom(4)
        applyCommands(commands)
        #timestamp last update

    except Exception as e:
        print("Broke connection to client:"+str(e))
