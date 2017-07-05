"""
Library to communicate with the Naze32 flight control board.
Receives telemetry data: angx, angy and heading
Transmits attitude commands: roll, pitch, yaw
"""

from __future__ import division
from pyMultiwii import MultiWii
import Adafruit_PCA9685, time

class DroneComm(object):
    """Handles communication to and from the drone.

    Receives data over the USB with Multiwii protocol
    Transmits data via an I2C interface to an Adafruit PWM generator

    Paramters
    ---------
    period: float
        pwm period (default 22ms)
    k_period: float
        pwm period calibration factor
    roll_pwm_trim: int
        roll channel trim (us)
    pitch_pwm_trim: int
        pitch channel trim (us)
    yaw_pwm_trim: int
        yaw channel trim (us)
    port: string
        usb port attached to flight control board (default "/dev/ttyUSB0")
        if None, assumes no input connection from flight control board
    """
    # Range of Values (Pulse Width): 1.1ms -> 1.9ms
    MIN_WIDTH = 0.0011
    MID_WIDTH = 0.0015
    MAX_WIDTH = 0.0019

    # time precision of feather pwm signal
    # each pwm cycle is divided into TICKS units of time
    TICKS = 4096

    # Featherboard channel map
    ROLL_CHANNEL  = 3
    PITCH_CHANNEL = 2
    YAW_CHANNEL   = 1

    # Calibration factor to compensate for mismatch between
    # requested pwm period and pwm freq implemented by Adafruit PWM generator
    # Useage:
    #     requested_period = K_PWM * target_period
    # when requesting a PWM signal with period target_period
    DEFAULT_K_PERIOD = 0.023 / 0.022 # 23ms/22ms

    def __init__(
            self, period=0.022, k_period=None,
            roll_pwm_trim=0, pitch_pwm_trim=0, yaw_pwm_trim=0,
            port="/dev/ttyUSB0"):
        self.period = period

        # store trims in units of seconds
        self.roll_pwm_trim  = roll_pwm_trim * 1E-6
        self.pitch_pwm_trim = pitch_pwm_trim * 1E-6
        self.yaw_pwm_trim   = yaw_pwm_trim * 1E-6

        if k_period is None:
            k_period = self.DEFAULT_K_PERIOD

        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(1./(k_period*period))
        if port is None:
            self.board = None
        else:
            self.board = MultiWii(port)

        self.reset_channels()

    def reset_channels(self):
        """Reset channels 0-6 on the feather board
        
        Applies trim to roll/pitch/yaw channels
        """
        for i in range(6):
            self.set_pwidth(i, self.MID_WIDTH)
        self.set_pwidth(
            self.ROLL_CHANNEL, self.MID_WIDTH + self.roll_pwm_trim)
        self.set_pwidth(
            self.PITCH_CHANNEL, self.MID_WIDTH + self.pitch_pwm_trim)
        self.set_pwidth(
            self.YAW_CHANNEL, self.MID_WIDTH + self.yaw_pwm_trim)

    def set_pwidth(self, channel, width):
        """Set a positive Pulse Width on a channel
        
        Parameters
        ----------
        channel: int
            pwm channel to set positive pulse width
        width: float
            positive pulse width (seconds)
        """
        width = width / self.period * self.TICKS
        pulse = int(round(width))
        self.pwm.set_pwm(channel, 0, pulse)

    def set_roll_pwidth(self, width):
        """Apply trim and set the pwm Roll signal's positive pulse width
        
        Parameters
        ----------
        width: float
            positive pulse width (seconds)
        """
        # apply trim offset
        width += self.roll_pwm_trim
        width, valid = self.validate_pwidth(width)
        self.set_pwidth(self.ROLL_CHANNEL, width)
        if not valid:
            print("WARNING: Roll out of range!")

    def set_pitch_pwidth(self, width):
        """Apply trim and set the pwm Pitch signal's positive pulse width
        
        Parameters
        ----------
        width: float
            positive pulse width (seconds)
        """
        # apply trim offset
        width += self.pitch_pwm_trim
        width, valid = self.validate_pwidth(width)
        self.set_pwidth(self.PITCH_CHANNEL, width)
        if not valid:
            print("WARNING: Pitch out of range!")

    def set_yaw_pwidth(self, width):
        """Apply trim and set the pwm Yaw signal's positive pulse width
        
        Parameters
        ----------
        width: float
            positive pulse width (seconds)
        """
        # apply trim offset
        width += self.yaw_pwm_trim
        width, valid = self.validate_pwidth(width)
        self.set_pwidth(self.YAW_CHANNEL, width)
        if not valid:
            print("WARNING: Yaw out of range!")

    def validate_pwidth(self, width):
        """Verifies that the PWM signals are in the accepted range.

        If not, the MAX_WIDTH or MIN_WIDTH is returned
        """
        if(width > self.MAX_WIDTH):
            return self.MAX_WIDTH, False
        elif(width < self.MIN_WIDTH):
            return self.MIN_WIDTH, False
        else:
            return width, True

    def get_data(self, arg):
        """
        Returns the Attitude telemetry data from the Naze32 flight controller

        param: MultiWii Object, {"angx", "angy", "heading"}
        return: {angx, angy, heading}
        """
        self.board.getData(MultiWii.ATTITUDE)

        if arg == 'angx' or arg == 'angy' or arg == 'heading':
            return self.board.attitude[arg]
        else:
            print("Invalid argument\n")
            self.board.closeSerial()

    def get_roll(self):
        """Returns the roll angle"""
        self.board.getData(MultiWii.ATTITUDE)
        return self.board.attitude["angx"]

    def get_pitch(self):
        """Returns the pitch angle"""
        self.board.getData(MultiWii.ATTITUDE)
        return self.board.attitude["angy"]

    def get_yaw(self):
        """Returns the yaw angle"""
        self.board.getData(MultiWii.ATTITUDE)
        return self.board.attitude["heading"]

    def exit(self):
        """
        Used to gracefully exit and close the serial port
        """
        self.reset_channels()
        self.board = MultiWii("/dev/ttyUSB0")
        self.board.closeSerial()

    def control_example(self):
        """
        Sets the Roll/Pitch/Yaw on the Naze32 flight controller
        to maximum then minimum pulse widths
        """
        self.reset_channels()
        time.sleep(1)

        self.set_yaw(self.MAX_WIDTH)
        self.set_pitch(self.MAX_WIDTH)
        self.set_roll(self.MAX_WIDTH)

        time.sleep(2)

        self.set_yaw(self.MIN_WIDTH)
        self.set_pitch(self.MIN_WIDTH)
        self.set_roll(self.MIN_WIDTH)

        time.sleep(2)
        self.reset_channels()