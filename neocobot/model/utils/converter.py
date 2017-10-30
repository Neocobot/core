from neocobot.error.error import MinorError
from neocobot.error.error_code import ErrorCodes

class converter:
    def convert_actuator_ids_into_set(self, actuator_ids):
        if type(actuator_ids) is set:
            actuator_ids = list(actuator_ids)
        if type(actuator_ids) is not list:
            actuator_ids = [actuator_ids]
        if type(actuator_ids) is list:
            actuator_ids = actuator_ids[:]
            actuator_ids_length = len(actuator_ids)
            for i in range(actuator_ids_length):
                if type(actuator_ids[i]) is int:
                    actuator_ids[i] = str(actuator_ids[i])
                #########################################################################################'''
                # if replace while'''
                #########################################################################################'''
                if type(actuator_ids[i]) is not str:
                    error_message = 'each actuator id must either be an integer or a string.'
                    raise MinorError(ErrorCodes.e001048, error_message)
        else:
            error_message = 'actuator_ids must be of type list.'
            raise MinorError(ErrorCodes.e001049, error_message)
        actuator_ids = set(actuator_ids)
        if actuator_ids_length != len(actuator_ids):
            error_message = 'every actuator id can only be used once in actuator_ids.'
            raise MinorError(ErrorCodes.e001050, error_message)
        for aid in actuator_ids:

            #########################################################################################'''
            # if replace while'''
            #########################################################################################'''

            if aid not in self.config.get_actuator_indices():
                error_message = '"' + str(aid) + '" is not an existing actuator id.'
                raise MinorError(ErrorCodes.e001051, error_message)
        return actuator_ids