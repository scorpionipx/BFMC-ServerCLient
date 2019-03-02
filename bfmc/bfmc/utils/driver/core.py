import logging
import spidev

from bfmc.version import __version__

LOGGER = logging.getLogger('crawler')
LOGGER.setLevel(logging.INFO)

NOB_TO_N = {0: 0, 1: 1, 2: 2, 3: 4, 4: 4, 5: 8, 6: 8, 7: 8, 8: 8}


class BFMCDriverBoardSTM:
    """BFMCDriverBoardSTM

        Class used to handle Crawler's Driver Board.
    """
    def __init__(self):
        self.SPI = spidev.SpiDev()
        self.__init_SPI__()

    def __init_SPI__(self):
        """__init_SPI__

            Initialize SPI module
        :return: None
        """

        self.SPI.open(0, 0)
        self.SPI.max_speed_hz = 1953000

    def send_spi_data(self, data):
        """send_spi_data

            Send specified data over SPI module.
        :param data: data to be sent
        :type data: list
        :return: None
        """
        # LOGGER.info("Sending SPI {}".format(len(data)))
        self.SPI.xfer(data)

    def send_spi_command(self, cmd_id, data):
        """send_spi_command

            Send SPI command.
        :param cmd_id: command's ID in range [0, 31]
        :type cmd_id: int
        :param data: list of 8 bits data to be sent, maximum 1024 bytes
        :type data: list of int
        :return: None
        """
        number_of_data_bytes = len(data)

        if number_of_data_bytes <= 7:
            extend = 0
            n = NOB_TO_N[number_of_data_bytes + 1]
            data_0_byte = False
            frame_length = 1 << n
        else:
            number_of_data_bytes += 1
            extend = 1
            n = (number_of_data_bytes & 0b1100000000) >> 8
            data_0_byte = number_of_data_bytes & 0xFF
            data_frame_length = number_of_data_bytes + 1
            frame_length = data_frame_length + 1

        LOGGER.info("FRAME L: {}".format(frame_length))
        header_byte = (cmd_id << 3) | (extend << 2) | n

        spi_data = [header_byte]

        if data_0_byte:
            spi_data.append(data_0_byte)

        spi_data.extend(data)
        if extend == 0:
            while len(spi_data) < frame_length:
                spi_data.append(0)

        # for spi_byte in spi_data:
        #     LOGGER.info("{0:08b}: {1} {2}".format(spi_byte, spi_byte, chr(spi_byte)))

        self.send_spi_data(spi_data)
