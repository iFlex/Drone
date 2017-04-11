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
STEP     = 1;
normDelay = 10;
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
    cn.sendto(st,(config["host"],config["port"]))
    if DEBUG == TRUE:
        print(str(THROTTLE)+" "+str(YAW)+" "+str(PITCH)+" "+str(ROLL))

def callback(event):
    frame.focus_set()
    print "clicked at", event.x, event.y

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
        global THROTTLE,PITCH,YAW,ROLL,cancelNext   
        while True:
            if cancelNext == 0:
                THROTTLE += getStep(THROTTLE,config["restval"]["THROTTLE"],STEP)
                PITCH += getStep(PITCH,config["restval"]["PITCH"],STEP)
                ROLL += getStep(ROLL,config["restval"]["ROLL"],STEP)
                YAW += getStep(YAW,config["restval"]["YAW"],STEP)
                sendCommands()
            else:
                cancelNext -= 1
            time.sleep(normDelay/1000.0)
    except Exception as e:
        print e
    
frame = Frame(root, width=100, height=100)
frame.bind("<Button-1>", callback)
frame.bind("<Key>", key)
frame.pack()

thread.start_new_thread(backToNominal,())
root.mainloop()
