import pigpio

pi = pigpio.pi()
print pi.get_PWM_frequency(10);
print pi.get_PWM_frequency(11);
print pi.get_PWM_frequency(13);
print pi.get_PWM_frequency(15);
