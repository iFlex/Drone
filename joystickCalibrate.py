import joystick
import json
import time
import thread

print("Reading Config")
with open('config.json', 'r') as f:
    config = json.load(f)

def updateFromJoystick(data):
    pass

js = joystick.list()

if len(js) == 0:
	print "Could not find a Joystick :("
else:
	choice = 0
	for i in range(len(js)):
		print str(i)+") "+str(js[i])
	if len(js) > 1:
		print "Select a joystick:"
		choice = input("#")

	j = joystick.init(config["JoyStickAxisMap"],joystick=choice)
	
	#Axis Discovery
	calibrate = True
	while calibrate:
		config["JoyStickAxisMap"] = joystick.discoverAxis()
		print config["JoyStickAxisMap"];
		c = raw_input("Re calibrate? (Y/N):")
		if not (c == 'Y'):
			calibrate = False

	joystick.start(updateFromJoystick)
	raw_input("Please move all axis to their extremes, you have 20 seconds")
	time.sleep(20)
	raw_input("Please leave your Joystick in its neutral position and press return")
	joystick.is_neutral([])
	joystick.stop()

	data = joystick.getCalibrationData()

	config["JoystickCalibration"] = {}
	config["JoystickCalibration"] = data

	#Save calibration data
	with open('config.json', 'w') as outfile:
	    json.dump(config, outfile, indent=4, sort_keys=True)

	raw_input("COMPLETE: Configuration was saved")
