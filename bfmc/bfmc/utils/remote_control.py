import logging
import threading
import serial
import time
import sys

from time import sleep

from bfmc.utils.client import Client
from bfmc.utils.rc_input import RemoteControl
from bfmc.utils.rc_utils import BRAKE_BUTTON, POWER_AXIS, STEERING_AXIS

LOGGER = logging.getLogger('bfmc')
LOGGER.setLevel(logging.INFO)


class RC:
    """

    """
    def __init__(self, ip, port, rc_device):
        """

        :param ip:
        :param port:
        :param rc_device:
        """
        self.connection = Client(ip, port)
        self.device = RemoteControl()
        self.device.init_rc_device(rc_device)

    def manual_control(self):
        """

        :return:
        """

        idle_counter = 0

        while True:
            self.device.__update_rc__()

            brake_button_pressed = int(self.device.joystick.get_button(BRAKE_BUTTON))
            power = -int(self.device.joystick.get_axis(POWER_AXIS) * 100)
            steering = int(self.device.joystick.get_axis(STEERING_AXIS) * 100) / 4.3

            if steering < -23:
                steering = -23
            if steering > 23:
                steering = 23

            if power < -100:
                power = -100
            if power > 100:
                power = 100

            LOGGER.info("B: {} P: {} S: {}".format(brake_button_pressed, power, steering))

            if steering == 0 and power == 0 and brake_button_pressed == 0:
                idle_counter += 1
                if idle_counter > 5:
                    sleep(.05)
                    continue
            else:
                idle_counter = 0

            if brake_button_pressed:
                rc.connection.send_package("$i13$d0")
                sleep(.05)
                continue

            rc.connection.send_package("$i10$d{} {}".format(power, steering))
            sleep(.05)


if __name__ == '__main__':
    rc = RC(
        ip='192.168.100.9',
        port=8888,
        rc_device="Controller (XBOX 360 For Windows)",
    )
    rc.connection.connect_to_host()
    sleep(1)
    rc.manual_control()
