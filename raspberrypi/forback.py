from motor_control import *
import time

GPIO.setmode(GPIO.BCM)
initMotor()

for spd in range(SPEED_MAX_FB):
    goForward(spd)
    time.sleep(0.1)

time.sleep(1)

stopMotor()

time.sleep(1)

for spd in range(SPEED_MAX_FB):
    goBackward(spd)
    time.sleep(0.1)

time.sleep(1)

stopMotor()

exitMotor()
GPIO.cleanup()