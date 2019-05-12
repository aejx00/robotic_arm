#!/usr/bin/env python3
from __future__ import division
import sys
import time
import curses
import curses.textpad
import Adafruit_PCA9685


pwm = Adafruit_PCA9685.PCA9685()
servo_min = 150  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096
pwm.set_pwm_freq(60)
servo_delay = .15
loop_delay = .035
arms = 0
increment = 8


# servo mapping
servo_numb = {"base": 0,
                   "ext_left": 1,
                   "ext_right": 2,
                   "elbow": 3,
                   "rotation": 4,
                   "wrist": 5,
                   "claw": 6 }


# set minimum, midpoint, and maximum positions for each servo
calibration = {"base": [150, 390, 600, 0], # def 390
               "ext_left": [295, 415, 535, 0], # old 390
               "ext_right": [505, 385, 265, 0], # old 430
               "elbow": [0, 590, 600, 0],
               "rotation": [150, 350, 600, 0], # 350
               "wrist": [500, 210, 150, 0], # def 500
               "claw": [395, 500, 600, 0] } # def 500


def set_servo_pulse(channel, pulse):
    pulse_length = 1000000  # 1,000,000 us per second
    pulse_length //= 60  # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096  # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)


def set_servo_value(servo_desc, position):
    """
    Set servo to value defined in calibration, update dict value
    :param servo_desc: servo key
    :param position: value contained in calibration
    :return: N/A
    """
    pwm.set_pwm(servo_numb[servo_desc], 0, calibration[servo_desc][position])
    calibration[servo_desc][3] = calibration[servo_desc][position]


def servo_increment(servo_desc, inc):
    """
    Increment servo by specific amount, and update dict value
    :param servo_desc: servo key
    :param inc: increment value
    :return: new servo value
    """
    new_val = calibration[servo_desc][3] + inc
    if 'ext' in servo_desc:
        return calibration[servo_desc][3]
    else:
        pwm.set_pwm(servo_numb[servo_desc], 0, new_val)
        calibration[servo_desc][3] = new_val
        return new_val


def arms_increment(inc):
    """
    Set predefined position for both ext servos, and update dict value
    :param inc: value defined in calibration dict
    :return: new value
    """
    global arms
    new_val = arms +inc
    if new_val > 2 or new_val < 0:
        return arms
    else:
        pwm.set_pwm(1, 0, calibration['ext_left'][new_val])
        pwm.set_pwm(2, 0, calibration['ext_right'][new_val])
        arms = new_val
        return arms


def idle():
    """
    Sets all servos to idle position
    :return: N/A
    """
    set_servo_value('claw', 2)
    time.sleep(servo_delay)
    set_servo_value('base', 1)
    time.sleep(servo_delay)
    set_servo_value('ext_left', 1)
    set_servo_value('ext_right', 1)
    arms = 1
    time.sleep(servo_delay)
    set_servo_value('elbow', 1)
    time.sleep(servo_delay)
    set_servo_value('rotation', 1)
    time.sleep(servo_delay)
    set_servo_value('wrist', 1)
    time.sleep(servo_delay)


def shutdown():
    """
    Sets all servos to shutdown position
    :return: N/A
    """
    pwm.set_pwm(0, 0, calibration['base'][1])
    time.sleep(servo_delay)
    pwm.set_pwm(3, 0, calibration['elbow'][2])
    time.sleep(servo_delay)
    pwm.set_pwm(1, 0, calibration['ext_left'][0])
    pwm.set_pwm(2, 0, calibration['ext_right'][0])
    time.sleep(servo_delay)
    pwm.set_pwm(4, 0, calibration['rotation'][1])
    time.sleep(servo_delay)
    pwm.set_pwm(5, 0, calibration['wrist'][1])
    time.sleep(servo_delay)
    pwm.set_pwm(6, 0, calibration['claw'][0])
    time.sleep(servo_delay)
    pwm.set_pwm(4, 0, calibration['rotation'][0])
    pwm.set_pwm(6, 0, calibration['claw'][2])
    time.sleep(servo_delay)
    pwm.set_pwm(4, 0, calibration['rotation'][2])
    time.sleep(servo_delay)
    pwm.set_pwm(4, 0, calibration['rotation'][1])
    pwm.set_pwm(6, 0, calibration['claw'][0])
    time.sleep(servo_delay)


if __name__ == '__main__':
    # setup curses keyboard input
    stdscr = curses.initscr()
    curses.noecho()
    try:
        idle()
        while True: # begin input loop
            key = stdscr.getch()
            if key == ord('w'):
                print(key, arms_increment(1))
                time.sleep(loop_delay)
            elif key == ord('s'):
                print(key, arms_increment(-1))
                time.sleep(loop_delay)
            elif key == ord('a'):
                print(key, servo_increment('base', 0 - increment))
                time.sleep(loop_delay)
            elif key == ord('d'):
                print(key, servo_increment('base', increment))
                time.sleep(loop_delay)
            elif key == ord('r'):
                print(key, servo_increment('claw', increment))
                time.sleep(loop_delay)
            elif key == ord('f'):
                print(key, servo_increment('claw', 0 - increment))
                time.sleep(loop_delay)
            elif key == ord('i'):
                print(key, servo_increment('elbow', increment))
                time.sleep(loop_delay)
            elif key == ord('j'):
                print(key, servo_increment('elbow', 0 - increment))
                time.sleep(loop_delay)
            elif key == ord('k'):
                print(key, servo_increment('rotation', increment))
                time.sleep(loop_delay)
            elif key == ord('l'):
                print(key, servo_increment('rotation', 0 - increment))
                time.sleep(loop_delay)
            elif key == ord('t'):
                print(key, servo_increment('wrist', increment))
                time.sleep(loop_delay)
            elif key == ord('g'):
                print(key, servo_increment('wrist', 0 - increment))
                time.sleep(loop_delay)
            elif key == ord('q'):
                print('exiting loop')
                break
            elif key == ord('z'):
                print('resetting to idle')
                idle()
    except NameError as e:
        print(e)
    finally:
        shutdown()
        pwm.set_all_pwm(0, 0)
        curses.endwin()

