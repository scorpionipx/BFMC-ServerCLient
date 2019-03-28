import logging
import threading

from time import sleep

from bfmc.utils.client import Client
from bfmc.utils.rc_input import RemoteControl
from bfmc.utils.rc_utils import BRAKE_BUTTON, POWER_AXIS, STEERING_AXIS, START_BUTTON, TURN_LEFT_SIGNAL_BUTTON, \
    TURN_RIGHT_SIGNAL_BUTTON, HAZARD_LIGHTS_BUTTON, LIGHTS_BUTTON, SPECIAL_CMD_BUTTON
from bfmc.utils.spi import build_spi_command

LOGGER = logging.getLogger('bfmc')
LOGGER.setLevel(logging.INFO)

LIGHTS_STATE_OFF = 0
LIGHTS_STATE_DIPPED_BEAM = 1
LIGHTS_STATE_HIGH_BEAM = 2
LIGHTS_STATE_RESET = 3

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
        self.device = RemoteControl()
        self.valid = self.device.init_rc_device(rc_device)
        if not self.valid:
            LOGGER.info('Remote control aborted!')
            return

        self.connection = Client(ip, port)

        self.lights_state = LIGHTS_STATE_OFF
        self.turning_signal_request = TURNING_SIGNAL_REQUEST_OFF

        self.lights_change_allowed = True
        self.turning_lights_change_allowed = True
        self.special_cmd_allowed = True

    def unlock_lights_change(self):
        """

        :return:
        """
        unlock_thread = threading.Thread(target=self.__unlock_lights_change_thread__)
        unlock_thread.start()

    def __unlock_lights_change_thread__(self, delay=0.35):
        """__unlock_lights_change_thread__

        :return:
        """
        sleep(delay)
        self.lights_change_allowed = True

    def unlock_turning_lights_change(self):
        """unlock_turning_lights_change

        :return:
        """
        unlock_thread = threading.Thread(target=self.__unlock_turning_lights_change_thread__)
        unlock_thread.start()

    def __unlock_turning_lights_change_thread__(self, delay=0.35):
        """__unlock_turning_lights_change_thread__

        :return:
        """
        sleep(delay)
        self.turning_lights_change_allowed = True

    def unlock_special_cmd(self):
        """unlock_turning_lights_change

        :return:
        """
        unlock_thread = threading.Thread(target=self.__unlock_special_cmd_thread__)
        unlock_thread.start()

    def __unlock_special_cmd_thread__(self, delay=1):
        """__unlock_special_cmd_thread__

        :return:
        """
        sleep(delay)
        self.special_cmd_allowed = True

    def manual_control(self):
        """

        :return:
        """
        LOGGER.info('Initiating remote control...')

        power_limit = 75
        steering_limit = 23
        idle_counter = 0

        for i in range(5):
            spi_data = build_spi_command(cmd_id=5, data=[LIGHTS_STATE_HIGH_BEAM])
            udp_frame = '$i50$d'
            for spi_data_value in spi_data:
                udp_frame += chr(spi_data_value)
            self.connection.send_package(udp_frame)
            sleep(.0512)
            spi_data = build_spi_command(cmd_id=5, data=[LIGHTS_STATE_OFF])
            udp_frame = '$i50$d'
            for spi_data_value in spi_data:
                udp_frame += chr(spi_data_value)
            self.connection.send_package(udp_frame)
            sleep(.0512)

        sleep(.5)

        LOGGER.info('Remote control initiated!')

        while True:
            self.device.__update_rc__()
            spi_data = None

            brake_button_pressed = int(self.device.joystick.get_button(BRAKE_BUTTON))
            start_button_pressed = int(self.device.joystick.get_button(START_BUTTON))

            lights_button_pressed = int(self.device.joystick.get_button(LIGHTS_BUTTON))
            turn_left_signal_button_pressed = int(self.device.joystick.get_button(TURN_LEFT_SIGNAL_BUTTON))
            turn_right_signal_button_pressed = int(self.device.joystick.get_button(TURN_RIGHT_SIGNAL_BUTTON))
            hazard_lights_button_pressed = int(self.device.joystick.get_button(HAZARD_LIGHTS_BUTTON))
            special_cmd_button_pressed = int(self.device.joystick.get_button(SPECIAL_CMD_BUTTON))

            if special_cmd_button_pressed:
                if self.special_cmd_allowed:
                    # LOGGER.info('Special CMD!')
                    # udp_frame = '$i1$d'
                    # _spi_data = build_spi_command(cmd_id=1, data=[13])
                    # for spi_data_value in _spi_data:
                    #     udp_frame += chr(spi_data_value)
                    # self.connection.send_package(udp_frame)
                    # sleep(.0512)
                    # self.special_cmd_allowed = False
                    # self.unlock_special_cmd()
                    # LOGGER.info('Special CMD done!')
                    udp_frame = '$i11$d0'
                    self.connection.send_package(udp_frame)
                    sleep(.5)

            if lights_button_pressed:
                if self.lights_change_allowed:
                    self.lights_state += 1
                    self.lights_state %= 3
                    spi_data = build_spi_command(cmd_id=5, data=[self.lights_state])
                    self.lights_change_allowed = False
                    self.unlock_lights_change()

            elif turn_left_signal_button_pressed:
                if self.turning_lights_change_allowed:
                    if self.turning_signal_request == TURNING_SIGNAL_REQUEST_LEFT:
                        spi_data = build_spi_command(cmd_id=4, data=[TURNING_SIGNAL_REQUEST_OFF])
                        self.turning_signal_request = TURNING_SIGNAL_REQUEST_OFF
                    else:
                        spi_data = build_spi_command(cmd_id=4, data=[TURNING_SIGNAL_REQUEST_LEFT])
                        self.turning_signal_request = TURNING_SIGNAL_REQUEST_LEFT
                    self.turning_lights_change_allowed = False
                    self.unlock_turning_lights_change()
            elif turn_right_signal_button_pressed:
                if self.turning_lights_change_allowed:
                    if self.turning_signal_request == TURNING_SIGNAL_REQUEST_RIGHT:
                        spi_data = build_spi_command(cmd_id=4, data=[TURNING_SIGNAL_REQUEST_OFF])
                        self.turning_signal_request = TURNING_SIGNAL_REQUEST_OFF
                    else:
                        spi_data = build_spi_command(cmd_id=4, data=[TURNING_SIGNAL_REQUEST_RIGHT])
                        self.turning_signal_request = TURNING_SIGNAL_REQUEST_RIGHT
                    self.turning_lights_change_allowed = False
                    self.unlock_turning_lights_change()
            elif hazard_lights_button_pressed:
                if self.turning_lights_change_allowed:
                    if self.turning_signal_request == TURNING_SIGNAL_REQUEST_HAZARD:
                        spi_data = build_spi_command(cmd_id=4, data=[TURNING_SIGNAL_REQUEST_OFF])
                        self.turning_signal_request = TURNING_SIGNAL_REQUEST_OFF
                    else:
                        spi_data = build_spi_command(cmd_id=4, data=[TURNING_SIGNAL_REQUEST_HAZARD])
                        self.turning_signal_request = TURNING_SIGNAL_REQUEST_HAZARD
                    self.turning_lights_change_allowed = False
                    self.unlock_turning_lights_change()
            else:
                pass

            if spi_data:
                udp_frame = '$i50$d'
                for spi_data_value in spi_data:
                    udp_frame += chr(spi_data_value)
                self.connection.send_package(udp_frame)

            power = -int(self.device.joystick.get_axis(POWER_AXIS) * power_limit)
            steering = int(self.device.joystick.get_axis(STEERING_AXIS) * steering_limit)

            if start_button_pressed:
                for i in range(5):
                    spi_data = build_spi_command(cmd_id=5, data=[LIGHTS_STATE_HIGH_BEAM])
                    udp_frame = '$i50$d'
                    for spi_data_value in spi_data:
                        udp_frame += chr(spi_data_value)
                    self.connection.send_package(udp_frame)
                    sleep(.0512)
                    spi_data = build_spi_command(cmd_id=5, data=[LIGHTS_STATE_OFF])
                    udp_frame = '$i50$d'
                    for spi_data_value in spi_data:
                        udp_frame += chr(spi_data_value)
                    self.connection.send_package(udp_frame)
                    sleep(.0512)

                sleep(.01)

                self.connection.send_package("stop_listening".format(power, steering))
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
                self.connection.send_package("$i13$d0")
                sleep(.05)
                continue

            self.connection.send_package("$i10$d{} {}".format(power, steering))
            sleep(.025)


if __name__ == '__main__':
    rc = RC(
        # ip='192.168.100.9',
        ip='192.168.0.102',
        port=8888,
        rc_device="Controller (XBOX 360 For Windows)",
    )
    if rc.valid:
        rc.connection.connect_to_host()
        sleep(1)
        rc.manual_control()
