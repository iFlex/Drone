import pygame.joystick
import time
import thread

axis_mapping = [];
extreme_values = [];
imperfection_offsets = [];

joystick = None
DO_CALIBRATE = True

def init(mapping):
	global axis_mapping, extreme_values, imperfection_offsets, joystick

	pygame.joystick.init()
	if pygame.joystick.get_count() == 0:
		return None;
	
	print "Number of joysticks:"+str(pygame.joystick.get_count())
	#Copy axis mapping
	axis_mapping = mapping
	
	#init joystick
	pygame.init()
	joystick = pygame.joystick.Joystick(0)
	joystick.init();
	
	#initialise final values
	for i in range(joystick.get_numaxes()):
		extreme_values.append([0,0]);
		imperfection_offsets.append(0.0)

	print "Axis count:"+str(joystick.get_numaxes());
	print "Joystick name:"+str(joystick.get_name());

def read_joystick():
	global joystick

	axes = joystick.get_numaxes()
	response = [0]*axes

	for i in range( axes ):
		response[i] = joystick.get_axis( i )
	
	return response;

def calibrate_step(values):
	global extreme_values
	
	for i in range(0,len(values)):
		if extreme_values[i][0] > values[i]:
			extreme_values[i][0] = values[i];
		if extreme_values[i][1] < values[i]:
			extreme_values[i][1] = values[i];

def format_response(values):
	global extreme_values, axis_mapping, imperfection_offsets

	response = {}
	for i in range(0,len(values)):
		delta = abs(extreme_values[i][1] - extreme_values[i][0])
		if(delta == 0):
			return {}
		
		rsp = abs(extreme_values[i][1] - values[i]) / delta
		response[axis_mapping[i]] = rsp + (1-abs(0.5-rsp)/0.5)*imperfection_offsets[i]

	print response
	return response;

def is_neutral(skip):
	global imperfection_offsets, joystick
	if joystick == None:
		return

	#Calculate impefcetion offsets
	if not (sum(imperfection_offsets) == 0):
		for i in range(0,len(imperfection_offsets)):
			imperfection_offsets[i] = 0

	v = read_joystick()
	p = format_response(v)
	for i in range(0,len(v)):
		if not (axis_mapping[i] in skip):
			imperfection_offsets[i] = 0.5 - p[axis_mapping[i]]

def stop_calibration():
	global DO_CALIBRATE
	DO_CALIBRATE = False

def start_calibration():
	global DO_CALIBRATE
	DO_CALIBRATE = True

def run(callback):
	global DO_CALIBRATE
	done = False;
	while done == False:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done=True    
		
		data = read_joystick()
		if DO_CALIBRATE:
			calibrate_step(data)
		callback(format_response(data))

		time.sleep(0.20);

def start(callback):
	global joystick
	if joystick != None:
		thread.start_new_thread(run,(callback,))
		return True
	else:
		return False
