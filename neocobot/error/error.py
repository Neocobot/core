'''
@Project: Neocobot

@Created: 06-June-2017 by Chen Zhuo


This file contains all MyP exception classes.
Also a complete list of all assertions and errors is defined within this file.
'''
import inspect
import os

from neocobot.log.log import Log

from neocobot.error.error_code import ErrorCodes


class RobotError(Exception):
    __qualname__ = 'RobotError'

    def __init__(self, error_code, message_text, message_title, message_level, message_type, status=Log.ERROR):
        if type(error_code) is not ErrorCodes.Code:
            assertion_message = 'parameter "error_code" has to be an error code of the ErrorCodes class.'
            raise ProgramError(ErrorCodes.e000001, assertion_message, 'Program Error')
        self.error_code = error_code
        self.message_text = message_text
        self.message_title = message_title
        self.message_level = message_level
        self.message_type = message_type
        Log.write(status, '(code:' + error_code.code + '): ' + message_title + ', ' + message_text)


class CriticalError(RobotError):
    __qualname__ = 'CriticalError'

    def __init__(self, robot_context, error_code, message_text, message_title='Critical Error'):
        RobotError.__init__(self, error_code, message_text, message_title, 4, 2)
        robot_context.status.set_status_error(True)
        robot_context.error_handling_thread.start_queue.put(None)

class MinorError(RobotError):
    __qualname__ = 'MinorError'

    def __init__(self, error_code, message_text, message_title='Minor Error'):
        RobotError.__init__(self, error_code, message_text, message_title, 2, 2)

class ProgramError(RobotError):
    __qualname__ = 'ProgramError'

    def __init__(self, error_code, message_text, message_title='Program Error'):
        file_path = os.path.abspath(inspect.stack()[1][1])
        file_name = os.path.split(file_path)[1]
        RobotError.__init__(self, error_code, message_text, message_title, 3, 2)


class ConfigError(RobotError):
    __qualname__ = 'ConfigError'

    def __init__(self, error_code, message_text, message_title='Config Error'):
        RobotError.__init__(self, error_code, message_text, message_title, 2, 2)

class CommunicationError(RobotError):
    __qualname__ = 'CommunicationError'
    __doc__ = '\n    error that is supposed to be raised if a CAN bus connection error occurs.\n    a CriticalError is later raised by the control board.\n    '

    def __init__(self, error_code, message_text, message_title='Communication Error'):
        RobotError.__init__(self, error_code, message_text, message_title, 4, 2)

class DatabaseError(RobotError):
    __qualname__ = 'DatabaseError'

    def __init__(self, error_code, message_text, message_title='Database Error'):
        RobotError.__init__(self, error_code, message_text, message_title, 3, 2)

class ScriptError(RobotError):
    __qualname__ = 'ScriptError'

    def __init__(self, error_code, message_text, message_title='Script Error'):
        RobotError.__init__(self, error_code, message_text, message_title, 2, 2)

class ShadowError(RobotError):
    __qualname__ = 'ShadowError'

    def __init__(self):
        RobotError.__init__(self, ErrorCodes.Code('e000000'), 'Terminate the running script', 'Shadow Error', 0, 0, status=Log.WARNING)

class AlgorithmError(RobotError):
    __qualname__ = 'AlgorithmError'

    def __init__(self, error_code, message_text, message_title='algorithm Error'):
        RobotError.__init__(self, error_code, message_text, message_title, 3, 2)

class ComponentError(RobotError):
    __qualname__ = 'ComponentError'

    def __init__(self, error_code, message_text, message_title='Component Error'):
        RobotError.__init__(self, error_code, message_text, message_title, 3, 2)

class SensorError(RobotError):
    __qualname__ = 'SensorError'

    def __init__(self, error_code, message_text, message_title='Sensor Error'):
        RobotError.__init__(self, error_code, message_text, message_title, 2, 2)

class KinematicError(RobotError):
    __qualname__ = 'KinematicError'

    def __init__(self, error_code, message_text, message_title='Kinematic Error'):
        RobotError.__init__(self, error_code, message_text, message_title, 3, 2)

class NetworkError(RobotError):
    __qualname__ = 'NetworkError'

    def __init__(self, error_code, message_text, message_title='Network Error'):
        RobotError.__init__(self, error_code, message_text, message_title, 2, 2)