import logging
import socket as py_socket

LOGGER = logging.getLogger('bfmc')
LOGGER.setLevel(logging.INFO)

DEFAULT_IP = 'localhost'
DEFAULT_PORT = 8888

ALLOWED_CONNECTIONS = 1
BUFFER_SIZE = 1024  # bytes

ENCODING = 'utf-8'

LOST_CONNECTION_PACKAGES_LIMIT = 25
LOST_CONNECTION_PACKAGE = ""


def get_local_machine_ip_addresses():
    """__get_local_machine_ip_addresses__

        Fetch a list of local's machine IP addresses.
    :return: list of IP addresses
    :rtype: list of str
    """
    ip_list = []
    try:
        ip_list.append([l for l in ([ip for ip in py_socket.gethostbyname_ex(py_socket.gethostname())[2]
                                     if not ip.startswith("127.")][:1],
                                    [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close())
                                      for s in [py_socket.socket(py_socket.AF_INET, py_socket.SOCK_DGRAM)]][0][1]])
                        if l][0][0])
    except Exception as err:
        error = "Couldn't fetch local machine's IP addresses! {}".format(err)
        LOGGER.error(error)

    return ip_list
