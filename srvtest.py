import RPi.GPIO as GPIO
import time

servo_pin = 18  # GPIO pin you connected
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

pwm = GPIO.PWM(servo_pin, 50)  # 50 Hz
pwm.start(0)

try:
    for angle in [0, 45, 90, 135, 180]:
        duty = 2.5 + (angle / 180) * 10  # convert angle to duty cycle
        pwm.ChangeDutyCycle(duty)
        print(f"Angle: {angle}, Duty: {duty}")
        time.sleep(1)
finally:
    pwm.stop()
    GPIO.cleanup()
