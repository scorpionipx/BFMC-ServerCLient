import logging
import pygame

from time import sleep

from bfmc.utils.rc_utils import *


LOGGER = logging.getLogger('bfmc')
LOGGER.setLevel(logging.INFO)


class RemoteControl:
    """RemoteControl

        Class used to handle remote control input devices.
    """
    def __init__(self):
        """

        """
        self.rc_driver_enabled = False
        self.joystick = None

        self.__init_rc_drivers__()

    def __init_rc_drivers__(self):
        """__init_rc_drivers__

            Init drivers required for rc input devices.
        :return: initialization result
        :rtype: bool
        """
        LOGGER.info("Initializing RC drivers...")
        try:
            pygame.init()
            pygame.joystick.init()
            self.rc_driver_enabled = True
        except Exception as err:
            LOGGER.info("Failed to initialize RC drivers! {}".format(err))
            self.rc_driver_enabled = False
            return False
        LOGGER.info("RC drivers initialed!")
        return True

    def init_rc_device(self, rc_device=None):
        """init_rc_device

        :param rc_device:
        :return: RC device initializing result
        :rtype: bool
        """
        if not rc_device:
            return False

        for joystick, joystick_index in self.get_joysticks():
            if joystick == rc_device:
                LOGGER.info("Initialing controls for {}...".format(rc_device))
                self.joystick = pygame.joystick.Joystick(joystick_index)
                self.joystick.init()

                if not self.joystick.get_name() == rc_device:
                    LOGGER.error("Invalid joystick indexing!")
                    return False

                load_rc_configuration(rc_device)

                LOGGER.info("Successfully initialized {}!".format(rc_device))
                return True

    def get_joysticks(self):
        """get_joysticks

            Get the list of available joysticks and their index.
        :return: list of available joysticks
        :rtype: list of tuple
        """
        LOGGER.info("Scanning for joysticks...")
        joystick_count = pygame.joystick.get_count()
        LOGGER.info("Available joysticks: {}".format(joystick_count))
        joystick_names = []
        for joystick_index in range(joystick_count):
            joystick = pygame.joystick.Joystick(joystick_index)
            joystick.init()
            joystick_name = joystick.get_name()
            joystick_names.append((joystick_name, joystick_index))
            LOGGER.info("{}) {}".format(joystick_index + 1, joystick_name))

        return joystick_names

    def test_rc(self, input_device=None):
        """test_rc

        :return:
        """
        if not input_device:
            return

        if not self.init_rc_device(input_device):
            return False

        number_of_buttons = self.joystick.get_numbuttons()
        LOGGER.info("Number of buttons: {}".format(number_of_buttons))
        number_of_axis = self.joystick.get_numaxes()
        LOGGER.info("Number of axis: {}".format(number_of_axis))
        button_pressed = [False] * number_of_buttons

        while True:
            self.__update_rc__()

            for button_index in range(number_of_buttons):
                if self.joystick.get_button(button_index):
                    button_pressed[button_index] = True
                    LOGGER.info("Button {} pressed!".format(button_index))
                else:
                    button_pressed[button_index] = False

            for axis_index in range(number_of_axis):
                axis = int(self.joystick.get_axis(axis_index) * 100)
                if axis != 0:
                    LOGGER.info("AXIS {}: {}".format(axis_index, axis))

            sleep(.05)

    def __update_rc__(self):
        """

        :return:
        """
        pygame.event.pump()


if __name__ == '__main__':
    rc = RemoteControl()
    rc.test_rc("Controller (XBOX 360 For Windows)")

