import logging
import pygame

from bfmc.version import __version__


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

    def get_joysticks(self):
        """get_joysticks

            Get the list of available joysticks.
        :return: list of available joysticks
        :rtype: list of str
        """
        LOGGER.info("Scanning for joysticks...")
        joystick_count = pygame.joystick.get_count()
        LOGGER.info("Available joysticks: {}".format(joystick_count))

    def test_rc(self):
        """test_rc

        :return:
        """
        pass


if __name__ == '__main__':
    rc = RemoteControl()
