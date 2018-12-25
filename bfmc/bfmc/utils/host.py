import logging
import threading
import socket as py_socket

from time import sleep

from bfmc.utils.connection_utils import *


LOGGER = logging.getLogger('bfmc')
LOGGER.setLevel(logging.INFO)


class Host:
    """Host
    
        Class used to handle Crawler's server application.
    """
    def __init__(self, ip, port):
        """Constructor
        :param ip: Crawler's server IP address
        :type ip: str
        :param port: Crawler's communication port
        :type port: int
        """
        self.__ip__ = ip
        self.__port__ = port

        self.__connection__ = None
        self.__client__ = None

        self.server_is_on = False
        self.echo_mode_on = False
        self.listening = False

        self.encoding = ENCODING

    def start_server(self):
        """start_server

            Start Crawler's server.
        :return: starting server result
        :rtype: bool
        """
        LOGGER.info("Starting Crawler's server...")
        try:
            self.__connection__ = py_socket.socket(py_socket.AF_INET, py_socket.SOCK_STREAM)
            self.__connection__.bind(("", self.__port__))
        except Exception as err:
            error = "Failed to start Crawler's server! {}".format(err)
            LOGGER.error(error)
            return False

        self.__connection__.listen(ALLOWED_CONNECTIONS)
        self.server_is_on = True

        machine_ips = get_local_machine_ip_addresses()
        if len(machine_ips) > 0:
            LOGGER.info("Crawler's server is running and waiting for client connection!")
            LOGGER.info("HOSTNAME: {}".format(py_socket.gethostname()))

            for ip_index, machine_ip in enumerate(machine_ips):
                LOGGER.info("IP option #{}: {}".format(ip_index + 1, machine_ip))
            LOGGER.info("PORT: {}".format(self.__port__))
        else:
            LOGGER.info("Failed to retrieve local machine's IP address!")
            return False

        return True

    def stop_server(self):
        """stop_server

            Stop Crawler's server application
        :return: stopping server result
        :rtype: bool
        """
        LOGGER.info("Stopping Crawler's server...")
        try:
            self.__connection__.close()
        except Exception as err:
            error = "Failed to stop Crawler's server! {}".format(err)
            LOGGER.error(error)
            return False

        self.__connection__ = None
        self.server_is_on = False

        return True

    def __get_package_from_client__(self):
        """__get_package_from_client__

            Get a package from client.
        :return: package
        :rtype: bytearray
        """
        package = self.__client__.recv(BUFFER_SIZE)
        return package

    def echo(self):
        """echo

            Run server in echo mode.
        :return: None
        """
        if not self.server_is_on:
            self.start_server()
        if self.__client__ is None:
            self.connect_with_client()

        package_income_thread = threading.Thread(target=self.__echo__)
        self.echo_mode_on = True
        package_income_thread.start()

    def string_to_bytes(self, _string, encoding=None):
        """string_to_bytes

            Method converts string type to bytes, using specified encoding.
        Conversion is required for socket's data transfer protocol: string type is not supported.
        :param _string: string to be converted
        :param encoding: character encoding key
        :return: bytes(_string, encoding)
        """
        if encoding is None:
            encoding = self.encoding
        return bytes(_string, encoding)

    def send_package(self, package):
        """send_package

            Sends a package to the server.
        :param package: package to be sent
        :return: True if ok, error occurred otherwise
        """
        try:
            package = self.string_to_bytes(package)
            self.__client__.send(package)
            return True
        except Exception as err:
            error = "Error occurred while sending package to server: " + str(err)
            LOGGER.warning(error)
            return error

    def __echo__(self):
        """__echo__

            Thread echo.
        :return: None
        """
        lost_connection_packages_counter = 0
        while self.echo_mode_on:
            incoming_package = self.__get_package_from_client__()

            decoded_package = incoming_package.decode(encoding=ENCODING)
            LOGGER.info("echo mode - received package: {} - {}".format(decoded_package, len(decoded_package)))

            self.send_package(decoded_package)

            if decoded_package == LOST_CONNECTION_PACKAGE:
                LOGGER.info("echo mode - received null package")
                lost_connection_packages_counter += 1

                if lost_connection_packages_counter >= LOST_CONNECTION_PACKAGES_LIMIT:
                    LOGGER.info("Number of null packages received exceeded limit of {}!"
                                .format(LOST_CONNECTION_PACKAGES_LIMIT))
                    self.stop_echo()

                continue

            if 'stop echo' in decoded_package:
                self.stop_echo()

    def stop_echo(self):
        """echo

            Stop echo mode.
        :return: None
        """
        self.echo_mode_on = False
        LOGGER.info("Stopped echo mode!")

    def stop_listening(self):
        """stop_listening

            Stop listening to incoming packages.
        :return: None
        """
        self.listening = False

    def connect_with_client(self):
        """connect_with_client

            Connects with a requesting client.
        :return: None
        """
        timeout = 1000
        timeout_counter = 0
        client_is_valid = False

        LOGGER.info("Waiting for connection request... (timeout: {} seconds)".format(timeout / 100))
        while not client_is_valid:

            # establish a connection
            self.__client__, client_address = self.__connection__.accept()
            LOGGER.info("Got a connection request from {}".format(str(client_address[0])))

            client_is_valid = True
            LOGGER.info("Connected to {}!".format(client_address))

            if client_is_valid:
                pass
            else:
                LOGGER.info("Unknown client connection request! Connection refused!")
                self.__client__.shutdown(py_socket.SHUT_RDWR)
                self.__client__.close()
                self.__client__ = None

            sleep(.01)
            timeout_counter += 1
            if timeout_counter > timeout:
                LOGGER.info("Client connection timeout!")
                self.stop_listening()
                self.stop_server()
                break


if __name__ == '__main__':
    h = Host(DEFAULT_IP, DEFAULT_PORT)
    h.start_server()
    assert h.server_is_on
    h.echo()
    h.stop_server()
    assert not h.server_is_on
