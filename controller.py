from Tkinter import *
from socket import *
import json
import struct
import thread
import time

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

if THROTTLE == 0:
    THROTTLE = MIN

print("connecting to client @"+str(config["port"]))
cn = socket(AF_INET,SOCK_DGRAM)
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

def sendCommands():
    st = chr(THROTTLE)+chr(YAW)+chr(PITCH)+chr(ROLL)
    #cn.sendto(st,(config["host"],config["port"]))
    if DEBUG:
        print(str(THROTTLE)+" "+str(YAW)+" "+str(PITCH)+" "+str(ROLL))

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
    
    return step*sign

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
        print e
    
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

def updateSliders():
    global root,t,y,p,r
    t.set(THROTTLE)
    p.set(PITCH)
    y.set(YAW)
    r.set(ROLL)
    root.after(normDelay,updateSliders);

thread.start_new_thread(backToNominal,())
root.after(normDelay,updateSliders);
root.mainloop()
