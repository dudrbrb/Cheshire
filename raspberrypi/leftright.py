from motor_control import *
import time

GPIO.setmode(GPIO.BCM)
initMotor()

for spd in range(SPEED_MAX_FB):
    turnLeft(spd)
    time.sleep(0.1)

time.sleep(1)

stopMotor()

time.sleep(1)

for spd in range(SPEED_MAX_FB):
    turnRight(spd)
    time.sleep(0.1)

time.sleep(1)

stopMotor()

exitMotor()
GPIO.cleanup()