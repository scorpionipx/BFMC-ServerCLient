import threading

from time import sleep

from bfmc.utils.connection_utils import *
from bfmc.utils.host import Host

from bfmc.utils.serial_handler import SerialHandler
from bfmc.utils.save_encoder import SaveEncoder

from bfmc.utils.driver.core import BFMCDriverBoardSTM

LOGGER = logging.getLogger('bfmc')
LOGGER.setLevel(logging.INFO)


class BFMC:
    """BFMC

        Class used to handle BFMC remote controlled device.
    """

    def __init__(self, ip=None, port=DEFAULT_PORT):
        """Constructor
        """
        LOGGER.debug("Initializing BFMC...")
        self.lights_on = False
        print("ip: {}".format(ip))
        self.__ip__ = ip
        self.__port__ = port
        self.connection = Host(ip=self.__ip__, port=self.__port__)

        self.__listening__ = False

        self.driver = BFMCDriverBoardSTM()

        self.serial_handler = SerialHandler()
        self.serial_handler.startReadThread()

        self.e = SaveEncoder("Encoder.csv")
        self.e.open()

        self.ev1 = threading.Event()
        self.ev2 = threading.Event()

        LOGGER.info('Activating PID')
        self.serial_handler.readThread.addWaiter("PIDA", self.ev1, print)
        sent = self.serial_handler.sendPidActivation(True)
        if sent:
            confirmed = self.ev1.wait(timeout=1.0)
            if confirmed:
                print("Response was received!")
            else:
                raise ConnectionError('Response', 'Response was not received!')
        else:
            print("Sending problem")
            self.serial_handler.readThread.deleteWaiter("PIDA", self.ev1)

        self.serial_handler.readThread.addWaiter("MCTL", self.ev1, self.e.save)
        self.serial_handler.readThread.addWaiter("BRAK", self.ev1, self.e.save)
        self.serial_handler.readThread.addWaiter("ENPB", self.ev2, self.e.save)

        sent = self.serial_handler.sendEncoderPublisher()
        if sent:
            confirmed = self.ev1.wait(timeout=1.0)
            if confirmed:
                print("Deactivate encoder was confirmed!")
        else:
            raise ConnectionError('Response', 'Response was not received!')
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

        try:
            while self.connection.listening:
                    incoming_package = self.connection.__get_package_from_client__()
                    # LOGGER.info(incoming_package)
                    decoded_package = incoming_package.decode('utf-8')
                    # LOGGER.info("{}".format(decoded_package))

                    if 'stop_listening' in decoded_package:
                        self.connection.stop_listening()
                        self.connection.stop_server()
                        sleep(1)
                        self.connection = Host(ip=self.__ip__, port=self.__port__)
                        sleep(1)
                        self.listen()

                    if '$i' in decoded_package:
                        if '$d' in decoded_package:
                            self.decode_command(decoded_package)
        except Exception as err:
            error = 'Error occurred while listening! {}'.format(err)
            LOGGER.error(error)
            return
        except KeyboardInterrupt:
            LOGGER.info('Listening interrupted by user!')
            return

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
                sent = self.serial_handler.sendBrake(0.0)
                if sent:
                    confirmed = self.ev1.wait(timeout=1.0)
                    if confirmed:
                        LOGGER.info("Braking was confirmed!")
                    else:
                        LOGGER.error('Response', 'Response was not received!')
                else:
                    LOGGER.info("Sending problem")
            elif cmd_id == 10:
                power = float(data.split()[0])

                if power > 0:
                    power = 0.15
                elif power < 0:
                    power = -.15
                else:
                    power = 0

                steering = float(data.split()[1])
                LOGGER.info("MOVE({}, {})".format(power, steering))

                sent = self.serial_handler.sendMove(power, steering)
                if sent:
                    confirmed = self.ev1.wait(timeout=3.0)
                    if not confirmed:
                        LOGGER.info("Error getting confirmation via USART")
                else:
                    LOGGER.info("Error sending command via USART")
            elif cmd_id == 50:
                spi_data = []
                for char in data:
                    spi_data.append(ord(char))
                LOGGER.info('Sending SPI data: {}'.format(spi_data))
                self.driver.send_spi_data(spi_data)

            elif cmd_id == 1:
                spi_data = []
                for char in data:
                    spi_data.append(ord(char))
                LOGGER.info('CMD1: Sending SPI data: {}'.format(spi_data))
                self.driver.send_spi_data(spi_data)
                sleep(.001)
                LOGGER.info('Expecting SPI data...')
                received_data = self.driver.get_spi_data(buffer_size=1)
                LOGGER.info('Received SPI data: {}'.format(received_data))

        except Exception as err:
            LOGGER.info(err)
            pass

        # LOGGER.info("CMD_ID: {}".format(cmd_id))
        # LOGGER.info("DATA: {}".format(data))


