STEERING_AXIS = 0
POWER_AXIS = 3
BRAKE_BUTTON = 4
START_BUTTON = 7

LIGHTS_BUTTON = 3
TURN_LEFT_SIGNAL_BUTTON = 2
TURN_RIGHT_SIGNAL_BUTTON = 1
HAZARD_LIGHTS_BUTTON = 0


def load_rc_configuration(rc_device=None):
    """load_rc_configuration

    :param rc_device:
    :return:
    """
    if not rc_device:
        return False

    if rc_device == "Controller (XBOX 360 For Windows)":
        global STEERING_AXIS, POWER_AXIS, BRAKE_BUTTON
        STEERING_AXIS = 0
        POWER_AXIS = 3
        BRAKE_BUTTON = 4
        return True
