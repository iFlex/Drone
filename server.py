from socket import *
import pigpio
import json

pi = pigpio.pi()
cmdIndex = 0;
commands = [0,0,0,0]
config = []
DEBUG = False

print("Reading Config")
with open('config.json', 'r') as f:
    config = json.load(f)

print("Starting Server")
conn = socket(AF_INET,SOCK_STREAM)
conn.bind(('localhost',config["port"]))
conn.listen(1);

def applyCommands(cmds):
    global config
    if DEBUG == True:
        print("Applying commands:"+str(cmds))

    for c in cmds:
        if len(c) == 0:
            print "INVALID COMMAND:'"+c+"'"
            return
        
    pi.set_PWM_dutycycle(config["pins"]["THROTTLE"], ord(cmds[0]))
    pi.set_PWM_dutycycle(config["pins"]["YAW"], ord(cmds[1]))
    pi.set_PWM_dutycycle(config["pins"]["PITCH"], ord(cmds[2]))
    pi.set_PWM_dutycycle(config["pins"]["ROLL"], ord(cmds[3]))

while True:
    client = conn.accept()
    print("New connection:"+str(client[0]))
    controller = client[0];
    while True:
        try:
            byte = controller.recv(1)
            if len(byte) == 0:
                print ("Connection closed");
                break
            
	    commands[cmdIndex] = byte
            
            if cmdIndex == len(commands)-1:
                applyCommands(commands)
            cmdIndex += 1            
            cmdIndex %= 4

        except Exception as e:
	    print ("Broke connection to client:"+str(e))            
            controller.close()
            break
