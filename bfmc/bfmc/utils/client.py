import logging
import socket as py_socket

from bfmc.utils.connection_utils import *

LOGGER = logging.getLogger('bfmc')
LOGGER.setLevel(logging.INFO)


class Client:
    """Client
        Class used to handle internet connection on the crawler's controller as client(master).
    """

    def __init__(self, host, port=DEFAULT_PORT):
        """
            Constructor
        :param host: remote host's name or ip to connect to as string
                     example: '192.168.100.15'
        :param port: host's communication port as integer
                     example: 1369
        """
        try:
            LOGGER.debug("Initiating client...")

            # create the socket object
            self.socket = py_socket.socket(py_socket.AF_INET, py_socket.SOCK_STREAM)

            # setting host and port
            self.host = host
            self.port = port

            self.encoding = ENCODING

            LOGGER.debug("Client initiated!")

        except Exception as err:
            error = "Failed to initiate client! " + str(err)
            LOGGER.warning(error)

    def string_to_bytes(self, _string, encoding=None):
        """
            Method converts string type to bytes, using specified encoding.
        Conversion is required for socket's data transfer protocol: string type is not supported.
        :param _string: string to be converted
        :param encoding: character encoding key
        :return: bytes(_string, encoding)
        """
        if encoding is None:
            encoding = self.encoding
        return bytes(_string, encoding)

    def connect_to_host(self):
        """
            Method establishes connection to the host.
        :return: None
        """
        LOGGER.debug("Connecting to host...")
        self.socket.connect((self.host, self.port))
        LOGGER.debug("Connected to {}!".format(self.host))

    def send_package(self, package):
        """
            Sends a package to the server.
        :param package: package to be sent
        :return: True if ok, error occurred otherwise
        """
        try:
            package = self.string_to_bytes(package)
            self.socket.send(package)
            return True
        except Exception as err:
            error = "Error occurred while sending package to server: " + str(err)
            LOGGER.warning(error)
            return error

    def get_response(self):
        """get_response
            Get server's response.
        :return: None or server's response
        """
        try:
            response = self.socket.recv(BUFFER_SIZE)
        except Exception as err:
            LOGGER.warning(err)
            response = None
        return response

    def send_package_and_get_response(self, package):
        """send_package_and_get_response
            Method sends a package to the server and awaits a response.
        :return: None or server's response
        """
        self.send_package(package)
        response = self.get_response()
        return response


if __name__ == '__main__':
    c = Client(host='192.168.0.103', port=8888)
    c.connect_to_host()
    while 1:
        x = input()
        r = c.send_package_and_get_response(x)
        LOGGER.info("Resp: {}".format(r))
