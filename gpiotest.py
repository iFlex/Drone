import pigpio

pi = pigpio.pi()
pi.set_PWM_dutycycle(15, 255);
