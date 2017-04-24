import pygame.joystick
import time
import thread

axis_mapping = [];
extreme_values = [];
joytick = None

def init(mapping):
	global axis_mapping, extreme_values, joystick

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
	global extreme_values,axis_mapping

	response = {}
	for i in range(0,len(values)):
		delta = abs(extreme_values[i][1] - extreme_values[i][0])
		if(delta == 0):
			return {}
		response[axis_mapping[i]] = abs(extreme_values[i][1] - values[i]) / delta

	return response;

def run(callback):
	done = False;
	while done == False:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done=True    
		
		data = read_joystick()
		calibrate_step(data)
		callback(format_response(data))

		time.sleep(0.20);

def start(callback):
	if joystick != None:
		thread.start_new_thread(run,(callback,))
		return True
	else:
		return False
