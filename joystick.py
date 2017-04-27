import time
import thread
from threading import Thread
import pygame.joystick

axis_mapping = [];
extreme_values = [];
imperfection_offsets = [];

joystick = None
DO_CALIBRATE = True
CALIBRATE_TIME = 10

def list():
	global joystick
	
	if joystick == None:
		pygame.init()
		pygame.joystick.init()
	
	js = []
	r = pygame.joystick.get_count()
	
	for i in range(r):
		jstk = pygame.joystick.Joystick(i)
		jstk.init()
		js.append(jstk.get_name()+" With "+str(jstk.get_numaxes())+" axis")
	
	if joystick == None:
		pygame.quit()
	
	return js

def init(mapping,**kwargs):
	global axis_mapping, extreme_values, imperfection_offsets, joystick, DO_CALIBRATE
	choice = 0

	if "joystick" in kwargs.iteritems():
		choice = kwargs.iteritems()["joystick"]
	
	pygame.init()
	pygame.joystick.init()
	if pygame.joystick.get_count() == 0:
		return None;
	
	print "Number of joysticks:"+str(pygame.joystick.get_count())
	#Copy axis mapping
	axis_mapping = mapping
	
	#init joystick
	joystick = pygame.joystick.Joystick(choice)
	joystick.init();
	
	#initialise final values
	for i in range(joystick.get_numaxes()):
		extreme_values.append([0,0]);
		imperfection_offsets.append(0.0)

	if "calibration" in kwargs.iteritems() and kwargs.iteritems()["calibration"]:
		extreme_values = kwargs.iteritems()["calibration"]["boundaries"]
		imperfection_offsets = kwargs.iteritems()["calibration"]["offsets"]
		DO_CALIBRATE = False

	print "Axis count:"+str(joystick.get_numaxes());
	print "Joystick name:"+str(joystick.get_name());
	return joystick

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

done = False;
def run(callback):
	global DO_CALIBRATE,done
	while done == False:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done=True    
		
		data = read_joystick()
		if DO_CALIBRATE:
			calibrate_step(data)
		callback(format_response(data))

		time.sleep(0.10);

def start(callback):
	global joystick
	if joystick != None:
		thread.start_new_thread(run,(callback,))
		return True
	else:
		return False

def stop():
	global done
	done = True
	pygame.quit()

STOP_DISCOVERY = False	
def discoverMovedAxis():
	global STOP_DISCOVERY
	previous = []
	mdiff = 0
	axis = 0
			
	while not STOP_DISCOVERY:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				break

		data = read_joystick();
		if len(previous) != 0:
			for i in range(len(data)):
				diff = abs(data[i] - previous[i])
				if diff > mdiff:
					mdiff = diff
					axis = i
		previous = data
		time.sleep(0.10)
	return axis

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs, Verbose)
        self._return = None
    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args,
                                                **self._Thread__kwargs)
    def join(self):
        Thread.join(self)
        return self._return

def discoverAxis():
	global STOP_DISCOVERY
	#initialise final values
	mapping = [""]*joystick.get_numaxes();

	for i in range(joystick.get_numaxes()):
		axis = raw_input("Type the name of the axis you want to move next?(CAPITALS):");
		print ("Move axist to both maximums, you have "+str(CALIBRATE_TIME)+" seconds...");
		STOP_DISCOVERY = False
		thread = ThreadWithReturnValue(target=discoverMovedAxis)
		thread.start()
		time.sleep(CALIBRATE_TIME);
		STOP_DISCOVERY = True
		j = thread.join()

		if j >= 0 and j < len(mapping):
			mapping[j] = axis
			print mapping

	return mapping

def getCalibrationData():
	return {"boundaries":extreme_values,"offsets":imperfection_offsets}