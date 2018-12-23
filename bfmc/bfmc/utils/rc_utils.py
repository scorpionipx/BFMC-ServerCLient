STEERING_AXIS = -1
POWER_AXIS = -1
BRAKE_BUTTON = -1


def load_rc_configuration(rc_device=None):
    """load_rc_configuration

    :param rc_device:
    :return:
    """
    if not rc_device:
        return False

    if rc_device == "Controller (XBOX 360 For Windows)":
        STEERING_AXIS = 0
        POWER_AXIS = 3
        BRAKE_BUTTON = 4
        return True
