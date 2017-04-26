from Tkinter import *
from socket import *
import json
import struct
import thread
import time
import datetime
#import joystick

print("Reading Config")
with open('config.json', 'r') as f:
    config = json.load(f)

DEBUG = True

MAX      = config["MAXVAL"];
MIN      = config["MINVAL"];

THROTTLE = config["restval"]["THROTTLE"]
PITCH    = config["restval"]["PITCH"]
YAW      = config["restval"]["YAW"]
ROLL     = config["restval"]["ROLL"]
STEP     = 2;
normDelay = 5;
cancelNext = 0;
lastRemoteFeedback = datetime.datetime.now()

if THROTTLE == 0:
    THROTTLE = MIN

print("connecting to client @"+str(config["port"]))
cn = socket(AF_INET,SOCK_DGRAM)
cn.bind(('',config["port"]))
print("connected")

root = Tk()

def updateLevels(ctl):
    global THROTTLE,PITCH,YAW,ROLL,MAX,MIN
    ctl = ctl[1:2]

    if DEBUG == TRUE:
        print("'"+ctl+"'")

    if ctl == config["keymap"]["THROTTLE_UP"]:
        THROTTLE += STEP
        if THROTTLE > MAX:
            THROTTLE = MAX
    if ctl == config["keymap"]["THROTTLE_DN"]:
        THROTTLE -= STEP
        if THROTTLE < MIN:
            THROTTLE = MIN

    if ctl == config["keymap"]["YAW_LEFT"]:
        YAW -= STEP
        if YAW < MIN:
            YAW = MIN
    if ctl == config["keymap"]["YAW_RIGHT"]:
        YAW += STEP
        if YAW > MAX:
            YAW = MAX

    if ctl == config["keymap"]["ROLL_LEFT"]:
        ROLL -= STEP
        if ROLL < MIN:
            ROLL = MIN
    if ctl == config["keymap"]["ROLL_RIGHT"]:
        ROLL += STEP
        if ROLL > MAX:
            ROLL = MAX


    if ctl == config["keymap"]["PITCH_UP"]:
        PITCH += STEP
        if PITCH > MAX:
            PITCH = MAX
    if ctl == config["keymap"]["PITCH_DN"]:
        PITCH -= STEP
        if PITCH < MIN:
            PITCH = MIN
    
    if ctl == config["keymap"]["TMAX"]:
        THROTTLE = MAX;
    if ctl == config["keymap"]["TMIN"]:
        THROTTLE = MIN;

    if ctl == config["keymap"]["JOYSTICK_NORMAL"]:
        joystick.is_neutral(["THROTTLE"])

def sendCommands():
    st = chr(THROTTLE)+chr(YAW)+chr(PITCH)+chr(ROLL)
    cn.sendto(st,(config["host"],config["port"]))
    if DEBUG:
        print("T:"+str(THROTTLE)+" Y:"+str(YAW)+" P:"+str(PITCH)+" R:"+str(ROLL))

def lock(event):
    global cancelNext
    cancelNext = -1;
    
def release(event):
    global cancelNext
    cancelNext = 0

def key(event):
    global cancelNext
    cancelNext = 15;
    updateLevels(repr(event.char))
    sendCommands()

def getStep(current,goal,maxstp):
    if goal == 0:
        return 0
    
    step =  goal - current 
    sign = 1
    if step < 0:
        sign = -1
        step = -step
        
    if step > maxstp:
       step = maxstp
    
    return(step*sign)

def updateFromJoystick(values):
    global THROTTLE,PITCH,YAW,ROLL

    delta = MAX - MIN
    def normalise(val,invert):
        if invert == True:
            val = 1 - val
        return int(MIN + delta*val)

    try:
        if not (config["JoyStickAxisModifiers"]["THROTTLE"] == "IGNORE"):
            THROTTLE = normalise(values["THROTTLE"],config["JoyStickAxisModifiers"]["THROTTLE"] == "INVERT")
        
        if not (config["JoyStickAxisModifiers"]["PITCH"] == "IGNORE"):
            PITCH    = normalise(values["PITCH"],config["JoyStickAxisModifiers"]["PITCH"] == "INVERT")
        
        if not (config["JoyStickAxisModifiers"]["YAW"] == "IGNORE"):
            YAW      = normalise(values["YAW"],config["JoyStickAxisModifiers"]["YAW"] == "INVERT")
        
        if not (config["JoyStickAxisModifiers"]["ROLL"] == "IGNORE"):
            ROLL     = normalise(values["ROLL"],config["JoyStickAxisModifiers"]["ROLL"] == "INVERT")

    except Exception as e:
        print "ERROR: could not convert received joystick values. Potential reason (not finished calibration yet, move all axis to their extremes at least once"
        print e
        return

    sendCommands()
    
def backToNominal():
    try:
        global root,THROTTLE,PITCH,YAW,ROLL,cancelNext   
        while True:
            if cancelNext == 0:
                PITCH += getStep(PITCH,config["restval"]["PITCH"],STEP)
                ROLL += getStep(ROLL,config["restval"]["ROLL"],STEP)
                YAW += getStep(YAW,config["restval"]["YAW"],STEP)
            else:
                if cancelNext > 0:
                    cancelNext -= 1
            sendCommands()
            time.sleep(normDelay/1000.0)
    except Exception as e:
        print(e)
    
pwror = LabelFrame(root, width=500, height=500)
pirol = LabelFrame(root, width=500, height=500)

root.bind("<ButtonPress-1>",lock)
root.bind("<ButtonRelease-1>", release)
root.bind("<Key>", key)
pwror.pack()
pirol.pack()

def setThrottle(val):
    global THROTTLE
    THROTTLE = int(val)

def setYaw(val):
    global YAW
    YAW = int(val)

def setRoll(val):
    global ROLL
    ROLL = int(val)

def setPitch(val):
    global PITCH
    PITCH = int(val)

t = Scale(pwror, from_=MAX, to=MIN, command=setThrottle)
t.pack()

y = Scale(pwror, from_=MIN, to=MAX, orient=HORIZONTAL, command=setYaw)
y.pack()

p = Scale(pirol, from_=MAX, to=MIN, command=setPitch)
p.pack()

r = Scale(pirol, from_=MIN, to=MAX, orient=HORIZONTAL,command=setRoll)
r.pack()

def checkFeedback():
    global lastRemoteFeedback
    while True:
        data,address = cn.recvfrom(4)
        lastRemoteFeedback = datetime.datetime.now()
        
def updateSliders():
    global root,t,y,p,r
    t.set(THROTTLE)
    p.set(PITCH)
    y.set(YAW)
    r.set(ROLL)
    root.after(normDelay,updateSliders);

    nw = datetime.datetime.now();
    if ((nw - lastRemoteFeedback).total_seconds()*1000) > config["receiver_timeout"]:
        root.configure(background='red')
    else:
        root.configure(background='green')

joystick_connected = False
if "JoyStickAxisMap" in config and config["joystick"] == True:
    joystick.init(config["JoyStickAxisMap"])
    joystick_connected = joystick.start(updateFromJoystick)

if not joystick_connected:
    thread.start_new_thread(backToNominal,())

thread.start_new_thread(checkFeedback,())
root.after(normDelay,updateSliders);
root.mainloop()