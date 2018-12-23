import logging
import pygame
import threading

from time import sleep

from bfmc.utils.connection_utils import *
from bfmc.utils.host import Host

LOGGER = logging.getLogger('bfmc')
LOGGER.setLevel(logging.INFO)


class BFMC:
    """BFMC

        Class used to handle BFMC remote controlled device.
    """

    def __init__(self, ip=None, port=DEFAULT_PORT, manual_control=False):
        """Constructor
        """
        LOGGER.debug("Initializing BFMC...")
        self.lights_on = False
        print("ip: {}".format(ip))
        self.connection = Host(ip=ip, port=port)

        self.__listening__ = False
        LOGGER.debug("BFMC initialized!")

    def connect_with_client(self):
        """connect_with_client
            Connect with a client.
        :return: None
        """
        self.connection.connect_with_client()

    def echo(self):
        """echo
            Crawler echos back every data income from controller.
        :return: None
        """
        self.connection.echo()

    def listen(self):
        """listen
            Listen to incoming ethernet packages and execute commands.
        :return:
        """
        LOGGER.info("Listening to commands...")
        listen_thread = threading.Thread(target=self.__listen__)
        listen_thread.start()

    def __listen__(self):
        """__listen__

            Listen to incoming ethernet packages and execute commands thread.
        :return: None
        """
        if not self.connection.server_is_on:
            self.connection.start_server()

        if self.connection.__client__ is None:
            self.connection.connect_with_client()

        self.connection.listening = True

        while self.connection.listening:
            incoming_package = self.connection.__get_package_from_client__()
            # LOGGER.info(incoming_package)
            decoded_package = incoming_package.decode('utf-8')
            # LOGGER.info("{}".format(decoded_package))

            if 'stop_listening' in decoded_package:
                self.connection.stop_listening()

            if '$i' in decoded_package:
                if '$d' in decoded_package:
                    self.decode_command(decoded_package)

    def decode_command(self, package):
        """decode_command
            Transform UDP data to Crawler command.
        :param package: package received from client
        :type package: str
        :return:
        """
        cmd_id = package[package.find("$i") + 2:package.find("$d")]
        data = package[package.find("$d") + 2:]

        try:
            cmd_id = int(cmd_id)
            if cmd_id == 13:
                LOGGER.info("STOP")
                # stop
            elif cmd_id == 10:
                power = float(data.split()[0])
                steering = float(data.split()[1])
                LOGGER.info("MOVE({}, {})".format(power, steering))

        except Exception as err:
            LOGGER.info(err)
            pass

        # LOGGER.info("CMD_ID: {}".format(cmd_id))
        # LOGGER.info("DATA: {}".format(data))


