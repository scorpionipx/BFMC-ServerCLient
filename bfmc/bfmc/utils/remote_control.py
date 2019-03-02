import logging

from time import sleep

from bfmc.utils.client import Client
from bfmc.utils.rc_input import RemoteControl
from bfmc.utils.rc_utils import BRAKE_BUTTON, POWER_AXIS, STEERING_AXIS, START_BUTTON, TURN_LEFT_SIGNAL_BUTTON, \
    TURN_RIGHT_SIGNAL_BUTTON, HAZARD_LIGHTS_BUTTON, LIGHTS_BUTTON
from bfmc.utils.spi import build_spi_command

LOGGER = logging.getLogger('bfmc')
LOGGER.setLevel(logging.INFO)

LIGHTS_STATE_OFF = 0
LIGHTS_STATE_DIPPED_BEAM = 1
LIGHTS_STATE_HIGH_BEAM = 2

TURNING_SIGNAL_REQUEST_OFF = 0
TURNING_SIGNAL_REQUEST_LEFT = 1
TURNING_SIGNAL_REQUEST_RIGHT = 2
TURNING_SIGNAL_REQUEST_HAZARD = 3


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

        self.lights_state = LIGHTS_STATE_OFF
        self.turning_signal_request = TURNING_SIGNAL_REQUEST_OFF

    def manual_control(self):
        """

        :return:
        """

        power_limit = 75
        steering_limit = 23
        idle_counter = 0

        while True:
            self.device.__update_rc__()
            spi_data = None

            brake_button_pressed = int(self.device.joystick.get_button(BRAKE_BUTTON))
            start_button_pressed = int(self.device.joystick.get_button(START_BUTTON))

            lights_button_pressed = int(self.device.joystick.get_button(LIGHTS_BUTTON))
            turn_left_signal_button_pressed = int(self.device.joystick.get_button(TURN_LEFT_SIGNAL_BUTTON))
            turn_right_signal_button_pressed = int(self.device.joystick.get_button(TURN_RIGHT_SIGNAL_BUTTON))
            hazard_lights_button_pressed = int(self.device.joystick.get_button(HAZARD_LIGHTS_BUTTON))

            if lights_button_pressed:
                self.lights_state += 1
                self.lights_state %= 3
                spi_data = build_spi_command(cmd_id=5, data=[self.lights_state])
            elif turn_left_signal_button_pressed:
                if self.turning_signal_request == TURNING_SIGNAL_REQUEST_LEFT:
                    spi_data = build_spi_command(cmd_id=4, data=[TURNING_SIGNAL_REQUEST_OFF])
                else:
                    spi_data = build_spi_command(cmd_id=4, data=[TURNING_SIGNAL_REQUEST_LEFT])
            elif turn_right_signal_button_pressed:
                if self.turning_signal_request == TURNING_SIGNAL_REQUEST_RIGHT:
                    spi_data = build_spi_command(cmd_id=4, data=[TURNING_SIGNAL_REQUEST_OFF])
                else:
                    spi_data = build_spi_command(cmd_id=4, data=[TURNING_SIGNAL_REQUEST_RIGHT])
            elif hazard_lights_button_pressed:
                if self.turning_signal_request == TURNING_SIGNAL_REQUEST_HAZARD:
                    spi_data = build_spi_command(cmd_id=4, data=[TURNING_SIGNAL_REQUEST_OFF])
                else:
                    spi_data = build_spi_command(cmd_id=4, data=[TURNING_SIGNAL_REQUEST_HAZARD])
            else:
                pass

            if spi_data:
                rc.connection.send_package("$i50$d{}".format(spi_data))

            power = -int(self.device.joystick.get_axis(POWER_AXIS) * power_limit)
            steering = int(self.device.joystick.get_axis(STEERING_AXIS) * steering_limit)

            if start_button_pressed:
                rc.connection.send_package("stop_listening".format(power, steering))
                LOGGER.info("Remote control terminated!")
                break

            if steering < -steering_limit:
                steering = -steering_limit
            if steering > steering_limit:
                steering = steering_limit

            if power < -power_limit:
                power = -power_limit
            if power > power_limit:
                power = power_limit

            # LOGGER.info("B: {} P: {} S: {}".format(brake_button_pressed, power, steering))
            # LOGGER.info("P: {} S: {}".format(power, steering))

            if steering == 0 and power == 0 and brake_button_pressed == 0:
                idle_counter += 1
                if idle_counter > 5:
                    sleep(.025)
                    continue
            else:
                idle_counter = 0

            if brake_button_pressed:
                rc.connection.send_package("$i13$d0")
                sleep(.05)
                continue

            rc.connection.send_package("$i10$d{} {}".format(power, steering))
            sleep(.025)


if __name__ == '__main__':
    rc = RC(
        # ip='192.168.100.9',
        ip='192.168.0.106',
        port=8888,
        rc_device="Controller (XBOX 360 For Windows)",
    )
    rc.connection.connect_to_host()
    sleep(1)
    rc.manual_control()
