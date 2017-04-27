import joystick
import json
import time
import thread

print("Reading Config")
with open('config.json', 'r') as f:
    config = json.load(f)

def updateFromJoystick(data):
    print data

joystick.init(config["JoyStickAxisMap"])
config["JoyStickAxisMap"] = joystick.discoverAxis()
print config["JoyStickAxisMap"];
with open('config.json', 'w') as outfile:
    json.dump(config, outfile, indent=4, sort_keys=True)
