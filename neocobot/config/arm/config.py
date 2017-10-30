'''
@Project: Neocobot

@Created: 06-June-2017 by Chen Zhuo

This file loads the config data from the config files.
'''
import configparser
import inspect
import os

from neocobot.error.error import ConfigError, ProgramError
from neocobot.error.error_code import ErrorCodes


class Config:
    DEBUG = True

    def __init__(self, ctype):
        self.file_path = os.path.abspath(os.path.dirname(inspect.stack()[0][1]))
        self.ctype = ctype

        self.component_indices = []
        self.actuator_indices = []

        self.component_parameters = {}
        self.actuator_parameters = {}
        self.default_values = {}

    def read_config_data(self):
        pass

    @staticmethod
    def _read_parameter(config_type, config_parameter, config_file):
        if config_parameter not in config_file[config_type]:
            error_message = "parameter '" + str(config_parameter) + "' in [" + str(config_type) + '] could not be read.'
            raise ConfigError(ErrorCodes.e004001, error_message)
        return config_file[config_type][config_parameter]

    def get_file_path(self):
        return self.file_path

    def get_actuator_indices(self):
        return self.actuator_indices[:]

    def get_component_parameter(self, actuator_ids, parameter_name):
        parameters = None
        if type(actuator_ids) is set:
            parameters = {}
            for aid in actuator_ids:
                parameters[aid] = self.component_parameters[aid][parameter_name]
        elif type(actuator_ids) is list:
            parameters = []
            for aid in actuator_ids:
                parameters.append(self.component_parameters[aid][parameter_name])
        elif type(actuator_ids) is str:
            parameters = self.component_parameters[actuator_ids][parameter_name]
        else:
            error_message = 'wrong type for get component parameter function (should be set, list or string)'
            raise ConfigError(ErrorCodes.e004002, error_message)
        return parameters

    def get_actuator_parameter(self, actuator_ids, parameter_name):
        parameters = None
        if type(actuator_ids) is set:
            parameters = {}
            for aid in actuator_ids:
                parameters[aid] = self.actuator_parameters[aid][parameter_name]
        elif type(actuator_ids) is list:
            parameters = []
            for aid in actuator_ids:
                parameters.append(self.actuator_parameters[aid][parameter_name])
        elif type(actuator_ids) is str:
            parameters = self.actuator_parameters[actuator_ids][parameter_name]
        else:
            assertion_message = 'wrong type for get actuator parameter function (should be set, list or string)'
            raise ProgramError(ErrorCodes.e004003, assertion_message)
        return parameters

    def get_default_value(self, parameter_name):
        return self.default_values[parameter_name]

    def _read_component_parameters(self, component, component_category, actuator_id, file):
        pass

    def _read_actuator_parameters(self, component, actuator_id, file):
        pass


class ModelConfig(Config):
    __qualname__ = 'ModelConfig'

    # Loads the Configuration data
    def __init__(self, ctype):
        Config.__init__(self, ctype)
        self.model_config_file = None
        self.linear_axis_config_file = None
        self.general_config_file = None
        self.kinematic_indices = []
        self.linear_axis_indices = []

        self.link_indices = []

        self.link_parameters = {}
        self.impact_control_parameters = {}

        self.load_config_file()

    def load_config_file(self):
        try:
            self.init_model_config()
            self.init_axis_config()
            self.init_params_config()

            self.read_config_data()
        except ValueError:
            error_message = "variable type error in the file '" + self.ctype + "_model.config'."
            raise ConfigError(ErrorCodes.e004004, error_message)

    def init_model_config(self):
        file_name = 'model.config'
        try:
            model_path = os.path.normpath(os.path.join(self.file_path, file_name))
            self.model_config_file = configparser.ConfigParser(strict=True)
            self.model_config_file.read(model_path)
        except configparser.DuplicateOptionError:
            error_message = 'two parameters in "' + file_name + '" have the same name.'
            raise ConfigError(ErrorCodes.e004005, error_message)
        except configparser.DuplicateSectionError:
            error_message = 'two parameter sections in "' + file_name + '" have the same name.'
            raise ConfigError(ErrorCodes.e004006, error_message)
        except configparser.MissingSectionHeaderError:
            error_message = 'a section in "' + file_name + '" is missing.'
            raise ConfigError(ErrorCodes.e004007, error_message)

    def init_axis_config(self):
        file_name = 'linear_axis.config'
        try:
            model_path = os.path.normpath(os.path.join(self.file_path, file_name))
            self.linear_axis_config_file = configparser.ConfigParser(strict=True)
            self.linear_axis_config_file.read(model_path)
        except configparser.DuplicateOptionError:
            error_message = 'two parameters in "' + file_name + '" have the same name.'
            raise ConfigError(ErrorCodes.e004008, error_message)
        except configparser.DuplicateSectionError:
            error_message = 'two parameter sections in "' + file_name + '" have the same name.'
            raise ConfigError(ErrorCodes.e004009, error_message)
        except configparser.MissingSectionHeaderError:
            error_message = 'a section in "' + file_name + '" is missing.'
            raise ConfigError(ErrorCodes.e004010, error_message)

    def init_params_config(self):
        file_name = 'general_parameters.config'
        try:
            model_path = os.path.normpath(os.path.join(self.file_path, file_name))
            self.general_config_file = configparser.ConfigParser(strict=True)
            self.general_config_file.read(model_path)
        except configparser.DuplicateOptionError:
            error_message = 'two parameters in "' + file_name + '" have the same name.'
            raise ConfigError(ErrorCodes.e004011, error_message)
        except configparser.DuplicateSectionError:
            error_message = 'two parameter sections in "' + file_name + '" have the same name.'
            raise ConfigError(ErrorCodes.e004012, error_message)
        except configparser.MissingSectionHeaderError:
            error_message = 'a section in "' + file_name + '" is missing.'
            raise ConfigError(ErrorCodes.e004013, error_message)

    def get_config_file_by_component(self, category):
        if category == 'KINEMATIC_JOINT' or category == 'KINEMATIC_LINK':
            return self.model_config_file
        elif category == 'END_EFFECTOR':
            return self.end_effector_config_file
        elif category == 'LINEAR_AXIS':
            return self.linear_axis_config_file
        return None

    def read_config_data(self):
        if 'name' not in self.model_config_file['MODEL']:
            error_message = 'the model name is not defined in the config file.'
            raise ConfigError(ErrorCodes.e004014, error_message)
        model_name = self.model_config_file['MODEL']['name']
        if self.ctype != model_name:
            error_message = 'the model name needs to be the same as the file name.'
            raise ConfigError(ErrorCodes.e004015, error_message)

        component_categories = ['KINEMATIC_JOINT', 'KINEMATIC_LINK', 'LINEAR_AXIS']
        for component_category in component_categories:
            i = 1
            while True:
                if component_category is 'KINEMATIC_LINK':
                    component = component_category + '_' + str(i - 1) + str(i)
                else:
                    component = component_category + '_' + str(i)

                config_file = self.get_config_file_by_component(component_category)
                if component not in config_file:
                    break

                actuator_id = self._read_parameter(component, 'name', config_file)
                if actuator_id in self.component_indices:
                    error_message = 'actuator ids must be unique. "' + actuator_id + '" already exists.'
                    raise ConfigError(ErrorCodes.e004016, error_message)
                self.component_indices.append(actuator_id)
                self._read_component_parameters(component, component_category, actuator_id, config_file)
                self._read_parameters_by_category(component, component_category, actuator_id, config_file)

                i += 1

        axis_ids = set()
        for aid in self.get_actuator_indices():
            axis_ids.add(self.actuator_parameters[aid]['axis_id'])
        if len(self.get_actuator_indices()) != len(axis_ids):
            error_message = 'axis ids are not unique.'
            raise ConfigError(ErrorCodes.e004017, error_message)
        try:
            velocity_in_deg = self._read_parameter('DEFAULT_VALUE', 'velocity_in_deg', self.general_config_file)
            self.default_values['velocity_in_deg'] = float(velocity_in_deg)
            acceleration_in_deg = self._read_parameter('DEFAULT_VALUE', 'acceleration_in_deg', self.general_config_file)
            self.default_values['acceleration_in_deg'] = float(acceleration_in_deg)
            velocity_in_mm = self._read_parameter('DEFAULT_VALUE', 'velocity_in_mm', self.general_config_file)
            self.default_values['velocity_in_mm'] = float(velocity_in_mm)
            acceleration_in_mm = self._read_parameter('DEFAULT_VALUE', 'acceleration_in_mm', self.general_config_file)
            self.default_values['acceleration_in_mm'] = float(acceleration_in_mm)
        except ValueError:
            error_message = "default values in 'general_parameters.config' must be of type float."
            raise ConfigError(ErrorCodes.e004018, error_message)

    def _read_parameters_by_category(self, component, category, actuator_id, config_file):
        if category is 'KINEMATIC_JOINT':
            self.kinematic_indices.append(actuator_id)
            self._read_actuator_parameters(component, actuator_id, config_file)
            self._read_impact_control_parameters(component, actuator_id, config_file)
        elif category is 'KINEMATIC_LINK':
            self.link_indices.append(actuator_id)
            self._read_link_parameters(component, actuator_id, config_file)
        elif category is 'LINEAR_AXIS':
            self.linear_axis_indices.append(actuator_id)
            self._read_actuator_parameters(component, actuator_id, config_file)

    def _read_component_parameters(self, component, component_category, actuator_id, file):
        self.component_parameters[actuator_id] = {}
        self.component_parameters[actuator_id]['category'] = component_category
        component_type = str(self._read_parameter(component, 'type', file))
        if component_category == 'KINEMATIC_JOINT' and component_type not in ('WRIST', 'ELBOW'):
            error_message = "type of '" + component + "' needs to be either 'WRIST' or 'ELBOW'."
            raise ConfigError(ErrorCodes.e004019, error_message)
        self.component_parameters[actuator_id]['type'] = component_type

    def _read_actuator_parameters(self, component, actuator_id, file):
        self.actuator_indices.append(actuator_id)
        self.actuator_parameters[actuator_id] = {}
        axis_id = int(self._read_parameter(component, 'axis_id', file))
        if axis_id <= 0:
            error_message = "axis id of component '" + component + "' has to be a positive integer."
            raise ConfigError(ErrorCodes.e004020, error_message)
        self.actuator_parameters[actuator_id]['axis_id'] = axis_id
        current_limit = float(self._read_parameter(component, 'current_limit', file))
        if current_limit <= 0:
            error_message = "current limit of component '" + component + "' has to be a positive float."
            raise ConfigError(ErrorCodes.e004021, error_message)
        self.actuator_parameters[actuator_id]['current_limit'] = current_limit
        transmission_ratio = float(self._read_parameter(component, 'transmission_ratio', file))
        if transmission_ratio <= 0:
            error_message = "transmission ratio limit of component '" + component + "' has to be a positive float."
            raise ConfigError(ErrorCodes.e004022, error_message)
        self.actuator_parameters[actuator_id]['transmission_ratio'] = transmission_ratio
        encoder_resolution = float(self._read_parameter(component, 'encoder_resolution', file))
        if encoder_resolution <= 0:
            error_message = "encoder resolution limit of component '" + component + "' has to be a positive float."
            raise ConfigError(ErrorCodes.e004023, error_message)
        self.actuator_parameters[actuator_id]['encoder_resolution'] = encoder_resolution
        i_max_ps = float(self._read_parameter(component, 'i_max_ps', file))
        if i_max_ps <= 0:
            error_message = "i_max_ps limit of component '" + component + "' has to be a positive float."
            raise ConfigError(ErrorCodes.e004024, error_message)
        self.actuator_parameters[actuator_id]['i_max_ps'] = i_max_ps
        ts_s = float(self._read_parameter(component, 'ts_s', file))
        if ts_s <= 0:
            error_message = "ts_s limit of component '" + component + "' has to be a positive float."
            raise ConfigError(ErrorCodes.e004025, error_message)
        self.actuator_parameters[actuator_id]['ts_s'] = ts_s
        epc = self.actuator_parameters[actuator_id]['transmission_ratio']*self.actuator_parameters[actuator_id]['encoder_resolution']
        self.actuator_parameters[actuator_id]['epc'] = epc
        lower_angle_limit = float(self._read_parameter(component, 'lower_angle_limit', file))
        upper_angle_limit = float(self._read_parameter(component, 'upper_angle_limit', file))
        if lower_angle_limit >= upper_angle_limit:
            error_message = "lower angle limit of component '" + component + "' has to be smaller than upper angle limit."
            raise ConfigError(ErrorCodes.e004026, error_message)
        self.actuator_parameters[actuator_id]['lower_angle_limit'] = lower_angle_limit
        self.actuator_parameters[actuator_id]['upper_angle_limit'] = upper_angle_limit
        velocity_limit = float(self._read_parameter(component, 'velocity_limit', file))
        self.actuator_parameters[actuator_id]['velocity_limit'] = velocity_limit
        acceleration_limit = float(self._read_parameter(component, 'acceleration_limit', file))
        self.actuator_parameters[actuator_id]['acceleration_limit'] = acceleration_limit
        mounting_direction = int(self._read_parameter(component, 'mounting_direction', file))
        if abs(mounting_direction) != 1:
            error_message = "mounting direction of component '" + component + "' has to be either 1 or -1."
            raise ConfigError(ErrorCodes.e004027, error_message)
        self.actuator_parameters[actuator_id]['mounting_direction'] = mounting_direction
        mechanical_stop = int(self._read_parameter(component, 'mechanical_stop', file))
        if abs(mechanical_stop) != 1:
            error_message = "mechanical stop of component '" + component + "' has to be either 1 or -1."
            raise ConfigError(ErrorCodes.e004028, error_message)
        self.actuator_parameters[actuator_id]['mechanical_stop'] = mechanical_stop
        calibration_factor = float(self._read_parameter(component, 'calibration_factor', file))
        if calibration_factor <= 0 or calibration_factor > 1:
            error_message = "current factor of component '" + component + "' has to be within in range [0,1]."
            raise ConfigError(ErrorCodes.e004029, error_message)
        self.actuator_parameters[actuator_id]['calibration_factor'] = calibration_factor
        calibration_summand = float(self._read_parameter(component, 'calibration_summand', file))
        self.actuator_parameters[actuator_id]['calibration_summand'] = calibration_summand

    def _read_link_parameters(self, component, actuator_id, file):
        self.link_parameters[actuator_id] = {}
        length = float(self._read_parameter(component, 'length', file))
        if length < 0:
            error_message = "length of component '" + component + "' has to be positive."
            raise ConfigError(ErrorCodes.e004030, error_message)
        self.link_parameters[actuator_id]['length'] = length
        mass = float(self._read_parameter(component, 'mass', file))
        if mass < 0:
            error_message = "mass of component '" + component + "' has to be positive."
            raise ConfigError(ErrorCodes.e004031, error_message)
        self.link_parameters[actuator_id]['mass'] = mass
        center_of_mass = [float(self._read_parameter(component, 'CoM_x', file)), float(self._read_parameter(component, 'CoM_y', file)), float(self._read_parameter(component, 'CoM_z', file))]
        self.link_parameters[actuator_id]['CoM'] = center_of_mass

    def _read_impact_control_parameters(self, component, actuator_id, file):
        self.impact_control_parameters[actuator_id] = {}
        current_max_amplitude_without_payload = float(self._read_parameter(component, 'current_max_amplitude_without_payload', file))
        current_max_amplitude_with_max_payload = float(self._read_parameter(component, 'current_max_amplitude_with_max_payload', file))
        if current_max_amplitude_without_payload < 0 or current_max_amplitude_with_max_payload < 0:
            error_message = "current max amplitude for '" + component + "' has to be greater than 0."
            raise ConfigError(ErrorCodes.e004032, error_message)
        if current_max_amplitude_with_max_payload < current_max_amplitude_without_payload:
            error_message = "for current max amplitude of '" + component + "' max payload needs to be greater than without payload."
            raise ConfigError(ErrorCodes.e004033, error_message)
        self.impact_control_parameters[actuator_id]['current_max_amplitude_without_payload'] = current_max_amplitude_without_payload
        self.impact_control_parameters[actuator_id]['current_max_amplitude_with_max_payload'] = current_max_amplitude_with_max_payload
        current_velocity_offset = float(self._read_parameter(component, 'current_velocity_offset', file))
        if current_velocity_offset < 0:
            error_message = "current velocity offset for '" + component + "' has to be greater than 0."
            raise ConfigError(ErrorCodes.e004034, error_message)
        self.impact_control_parameters[actuator_id]['current_velocity_offset'] = current_velocity_offset
        current_deviation_without_payload = float(self._read_parameter(component, 'current_deviation_without_payload', file))
        current_deviation_with_max_payload = float(self._read_parameter(component, 'current_deviation_with_max_payload', file))
        if current_deviation_without_payload < 0 or current_deviation_with_max_payload < 0:
            error_message = "current max amplitude for '" + component + "' has to be greater than 0."
            raise ConfigError(ErrorCodes.e004035, error_message)
        if current_deviation_with_max_payload < current_deviation_without_payload:
            error_message = "for current deviation of '" + component + "' max payload needs to be greater than without payload."
            raise ConfigError(ErrorCodes.e004036, error_message)
        self.impact_control_parameters[actuator_id]['current_deviation_without_payload'] = current_deviation_without_payload
        self.impact_control_parameters[actuator_id]['current_deviation_with_max_payload'] = current_deviation_with_max_payload

    def get_kinematic_indices(self):
        return self.kinematic_indices[:]

    def get_linear_axis_indices(self):
        return self.linear_axis_indices[:]

    def get_link_indices(self):
        return self.link_indices[:]

    def get_link_parameter(self, link_id, parameter_name):
        return self.link_parameters[link_id][parameter_name]

    def get_kinematic_fingerprint(self):
        return [self.component_parameters[aid]['type'] for aid in self.get_kinematic_indices()]

    def get_impact_control_parameters(self):
        return self.impact_control_parameters.copy()


class HandConfig(Config):

    def __init__(self, ctype = None):
        Config.__init__(self, ctype)
        self.end_effector_indices = []
        self.end_effector_config_file = None
        self.end_effector_parameters = {}

        self.load_config_file()

    def load_config_file(self):
        file_name = ''
        try:
            file_name = 'end_effector.config'
            self.init_hand_config()
        except configparser.DuplicateOptionError:
            error_message = 'two parameters in "' + file_name + '" have the same name.'
            raise ConfigError(ErrorCodes.e004037, error_message)
        except configparser.DuplicateSectionError:
            error_message = 'two parameter sections in "' + file_name + '" have the same name.'
            raise ConfigError(ErrorCodes.e004038, error_message)
        except configparser.MissingSectionHeaderError:
            error_message = 'a section in "' + file_name + '" is missing.'
            raise ConfigError(ErrorCodes.e004039, error_message)

        self.read_config_data()

    def get_default_end_effector_id(self):
        return self.end_effector_indices[0]

    def get_end_effector_indices(self):
        return self.end_effector_indices[:]

    def get_end_effector_parameter(self, end_effector_id, parameter_name):
        return self.end_effector_parameters[end_effector_id][parameter_name]

    def init_hand_config(self):
        file_name = 'end_effector.config'
        model_path = os.path.normpath(os.path.join(self.file_path, file_name))
        self.end_effector_config_file = configparser.ConfigParser(strict=True)
        self.end_effector_config_file.read(model_path)

    def read_config_data(self):
        component_category = 'END_EFFECTOR'
        i = 1
        while True:
            config_file = self.end_effector_config_file
            component = component_category + '_' + str(i)
            if component not in config_file:
                break

            actuator_id = self._read_parameter(component, 'name', config_file)

            if actuator_id in self.component_indices:
                error_message = 'actuator ids must be unique. "' + actuator_id + '" already exists.'
                raise ConfigError(ErrorCodes.e004040, error_message)
            self.component_indices.append(actuator_id)

            self._read_component_parameters(component, component_category, actuator_id, config_file)
            self.end_effector_indices.append(actuator_id)
            if 'axis_id' in config_file[component]:
                self._read_actuator_parameters(component, actuator_id, config_file)
            self._read_end_effector_parameters(component, actuator_id, config_file)

            i += 1

        axis_ids = set()
        for aid in self.get_actuator_indices():
            axis_ids.add(self.actuator_parameters[aid]['axis_id'])
        if len(self.get_actuator_indices()) != len(axis_ids):
            error_message = 'axis ids are not unique.'
            raise ConfigError(ErrorCodes.e004041, error_message)

    def _read_end_effector_parameters(self, component, actuator_id, file):
        self.end_effector_parameters[actuator_id] = {}
        pose = [float(self._read_parameter(component, 'pose_x', file)), float(self._read_parameter(component, 'pose_y', file)), float(self._read_parameter(component, 'pose_z', file)), float(self._read_parameter(component, 'pose_roll', file)), float(self._read_parameter(component, 'pose_pitch', file)), float(self._read_parameter(component, 'pose_yaw', file))]
        self.end_effector_parameters[actuator_id]['pose'] = pose
        mass = float(self._read_parameter(component, 'mass', file))
        if mass < 0:
            error_message = "mass of component '" + component + "' has to be positive."
            raise ConfigError(ErrorCodes.e004042, error_message)
        self.end_effector_parameters[actuator_id]['mass'] = mass
        center_of_mass = [float(self._read_parameter(component, 'CoM_x', file)), float(self._read_parameter(component, 'CoM_y', file)), float(self._read_parameter(component, 'CoM_z', file))]
        self.end_effector_parameters[actuator_id]['CoM'] = center_of_mass
        max_payload = float(self._read_parameter(component, 'max_payload', file))
        if max_payload < 0:
            error_message = "maximum payload for '" + component + "' has to be greater than 0."
            raise ConfigError(ErrorCodes.e004043, error_message)
        self.end_effector_parameters[actuator_id]['max_payload'] = max_payload
        rotation_axis = [float(self._read_parameter(component, 'rotation_axis_x', file)), float(self._read_parameter(component, 'rotation_axis_y', file)), float(self._read_parameter(component, 'rotation_axis_z', file))]
        rotation_axis_length = sum(rotation_axis)
        if rotation_axis_length == 0:
            rotation_axis = []
        else:
            for i in range(len(rotation_axis)):
                if abs(rotation_axis[i]) > 1:
                    error_message = "the elements of rotation axis for '" + component + "' have to be between -1 and 1."
                    raise ConfigError(ErrorCodes.e004044, error_message)
                rotation_axis[i] /= rotation_axis_length
        self.end_effector_parameters[actuator_id]['rotation_axis'] = rotation_axis

    def _read_component_parameters(self, component, component_category, actuator_id, file):
        self.component_parameters[actuator_id] = {}
        self.component_parameters[actuator_id]['category'] = component_category
        component_type = str(self._read_parameter(component, 'type', file))
        self.component_parameters[actuator_id]['type'] = component_type

    def _read_actuator_parameters(self, component, actuator_id, file):
        self.actuator_indices.append(actuator_id)
        self.actuator_parameters[actuator_id] = {}
        axis_id = int(self._read_parameter(component, 'axis_id', file))
        if axis_id <= 0:
            error_message = "axis id of component '" + component + "' has to be a positive integer."
            raise ConfigError(ErrorCodes.e004045, error_message)
        self.actuator_parameters[actuator_id]['axis_id'] = axis_id
        current_limit = float(self._read_parameter(component, 'current_limit', file))
        if current_limit <= 0:
            error_message = "current limit of component '" + component + "' has to be a positive float."
            raise ConfigError(ErrorCodes.e004046, error_message)
        self.actuator_parameters[actuator_id]['current_limit'] = current_limit
        transmission_ratio = float(self._read_parameter(component, 'transmission_ratio', file))
        if transmission_ratio <= 0:
            error_message = "transmission ratio limit of component '" + component + "' has to be a positive float."
            raise ConfigError(ErrorCodes.e004047, error_message)
        self.actuator_parameters[actuator_id]['transmission_ratio'] = transmission_ratio
        encoder_resolution = float(self._read_parameter(component, 'encoder_resolution', file))
        if encoder_resolution <= 0:
            error_message = "encoder resolution limit of component '" + component + "' has to be a positive float."
            raise ConfigError(ErrorCodes.e004048, error_message)
        self.actuator_parameters[actuator_id]['encoder_resolution'] = encoder_resolution
        i_max_ps = float(self._read_parameter(component, 'i_max_ps', file))
        if i_max_ps <= 0:
            error_message = "i_max_ps limit of component '" + component + "' has to be a positive float."
            raise ConfigError(ErrorCodes.e004049, error_message)
        self.actuator_parameters[actuator_id]['i_max_ps'] = i_max_ps
        ts_s = float(self._read_parameter(component, 'ts_s', file))
        if ts_s <= 0:
            error_message = "ts_s limit of component '" + component + "' has to be a positive float."
            raise ConfigError(ErrorCodes.e004050, error_message)
        self.actuator_parameters[actuator_id]['ts_s'] = ts_s
        epc = self.actuator_parameters[actuator_id]['transmission_ratio']*self.actuator_parameters[actuator_id]['encoder_resolution']
        self.actuator_parameters[actuator_id]['epc'] = epc
        lower_angle_limit = float(self._read_parameter(component, 'lower_angle_limit', file))
        upper_angle_limit = float(self._read_parameter(component, 'upper_angle_limit', file))
        if lower_angle_limit >= upper_angle_limit:
            error_message = "lower angle limit of component '" + component + "' has to be smaller than upper angle limit."
            raise ConfigError(ErrorCodes.e004051, error_message)
        self.actuator_parameters[actuator_id]['lower_angle_limit'] = lower_angle_limit
        self.actuator_parameters[actuator_id]['upper_angle_limit'] = upper_angle_limit
        velocity_limit = float(self._read_parameter(component, 'velocity_limit', file))
        self.actuator_parameters[actuator_id]['velocity_limit'] = velocity_limit
        acceleration_limit = float(self._read_parameter(component, 'acceleration_limit', file))
        self.actuator_parameters[actuator_id]['acceleration_limit'] = acceleration_limit
        mounting_direction = int(self._read_parameter(component, 'mounting_direction', file))
        if abs(mounting_direction) != 1:
            error_message = "mounting direction of component '" + component + "' has to be either 1 or -1."
            raise ConfigError(ErrorCodes.e004052, error_message)
        self.actuator_parameters[actuator_id]['mounting_direction'] = mounting_direction
        mechanical_stop = int(self._read_parameter(component, 'mechanical_stop', file))
        if abs(mechanical_stop) != 1:
            error_message = "mechanical stop of component '" + component + "' has to be either 1 or -1."
            raise ConfigError(ErrorCodes.e004053, error_message)
        self.actuator_parameters[actuator_id]['mechanical_stop'] = mechanical_stop
        calibration_factor = float(self._read_parameter(component, 'calibration_factor', file))
        if calibration_factor <= 0 or calibration_factor > 1:
            error_message = "current factor of component '" + component + "' has to be within in range [0,1]."
            raise ConfigError(ErrorCodes.e004054, error_message)
        self.actuator_parameters[actuator_id]['calibration_factor'] = calibration_factor
        calibration_summand = float(self._read_parameter(component, 'calibration_summand', file))
        self.actuator_parameters[actuator_id]['calibration_summand'] = calibration_summand
