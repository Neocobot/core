'''
@Project: Neocobot

@Created: 06-June-2017 by Chen Zhuo
'''
import threading
import time
from math import sqrt

from neocobot.error.error import RobotError, MinorError
from scipy.signal import butter, filtfilt

from neocobot.error.error_code import ErrorCodes


class PathRecorder(threading.Thread):
    def __init__(self, arm):
        threading.Thread.__init__(self)
        self.arm = arm

    def run(self):
        self.arm.is_recording = True

        actuator_ids = self.arm.config.get_kinematic_indices()
        velocity_limits = self.arm.config.get_actuator_parameter(actuator_ids, 'velocity_limit')
        acceleration_limits = self.arm.config.get_actuator_parameter(actuator_ids, 'acceleration_limit')

        data = []
        initial_joint_angles = []
        time_interval = 0.1
        cycle_start = time.perf_counter()
        try:
            initial_joint_angles = self.arm.get_position(actuator_ids)
            while self.arm.is_recording:
                if self.arm.context.status.stop:
                    self.arm.is_recording = False
                    return
                joint_angles = self.arm.get_position(actuator_ids)
                while time.perf_counter() - cycle_start < time_interval:
                    time.sleep(0.001)
                cycle_start += time_interval
                data.append([joint_angles, time_interval])
        except RobotError as error:
            self.arm.is_recording = False
            raise error
        # 处理data数据
        while len(data) > 0 and max([abs(i - j) for (i, j) in zip(initial_joint_angles, data[0][0])]) < 0.1:
            data.pop(0)
        if len(data) > 0:
            terminal_joint_angles = data[-1][0]
            while len(data) > 1 and max([abs(i - j) for (i, j) in zip(terminal_joint_angles, data[-2][0])]) < 0.1:
                data.pop(-2)
        if len(data) < 7:
            error_message = 'path recording does not contain enough singular points (must be at least 7).'
            raise MinorError(ErrorCodes.e001007, error_message)
        for current_data in data:
            position = current_data[0]
            for i in range(len(actuator_ids)):
                while position[i] < self.arm.config.get_actuator_parameter(actuator_ids[i], 'lower_angle_limit') or \
                                position[i] > self.arm.config.get_actuator_parameter(actuator_ids[i],
                                                                                     'upper_angle_limit'):
                    error_message = 'the planned motion would put motor "' + actuator_ids[
                        i] + '" outside of its angle limit.'
                    raise MinorError(ErrorCodes.e001008, error_message)
        number_of_points = len(data)
        end = 0
        for i in range(len(data)):
            end += data[i][1]
        dt = end / float(number_of_points)
        nyf = 0.5 / dt
        for i in range(len(data[0][0])):
            y = []
            for j in range(len(data)):
                y.append(data[j][0][i])
            (b, a) = butter(4, 1.5 / nyf)
            try:
                filtered_angles = filtfilt(b, a, y)
            except ValueError:
                error_message = 'the recorded path was too short.'
                raise MinorError(ErrorCodes.e001009, error_message)
            for j in range(len(data)):
                data[j][0][i] = filtered_angles[j]
        velocity = [
            [abs(angle_i - angle_j) / data[0][1] for (angle_i, angle_j) in zip(data[0][0], initial_joint_angles)]]
        for i in range(len(data) - 1):
            velocity.append(
                [abs(angle_i - angle_j) / data[i + 1][1] for (angle_i, angle_j) in zip(data[i + 1][0], data[i][0])])
        velocity_ratios = []
        for i in range(len(actuator_ids)):
            velocity_ratios.append(max(velocity[i]) / velocity_limits[i])
        max_velocity_ratio = max(velocity_ratios)
        if max_velocity_ratio > 1:
            duration = data[0][1] * max_velocity_ratio
            if duration > 0.5:
                error_message = 'velocity too high. could not compensate by increasing duration between all points.'
                raise MinorError(ErrorCodes.e001010, error_message)
            else:
                warning_message = 'velocity too high. path was saved with longer duration between points.'
                self.interface.set_message_info(warning_message, 'Warning', 2, 2)
            for i in range(len(data)):
                data[i][1] = duration
            velocity = [
                [abs(angle_i - angle_j) / data[0][1] for (angle_i, angle_j) in zip(data[0][0], initial_joint_angles)]]
            for i in range(len(data) - 1):
                velocity.append(
                    [abs(angle_i - angle_j) / data[i + 1][1] for (angle_i, angle_j) in zip(data[i + 1][0], data[i][0])])
        acceleration = [[abs(speed_i) / data[0][1] for speed_i in velocity[0]]]
        for i in range(len(velocity) - 1):
            acceleration.append(
                [abs(speed_i - speed_j) / data[i + 1][1] for (speed_i, speed_j) in zip(velocity[i + 1], velocity[i])])
        acceleration_ratios = []
        for i in range(len(actuator_ids)):
            acceleration_ratios.append(max(acceleration[i]) / acceleration_limits[i])
        max_acceleration_ratio = max(acceleration_ratios)
        if max_acceleration_ratio > 1:
            duration = data[0][1] * sqrt(max_acceleration_ratio)
            if duration > 0.5:
                error_message = 'acceleration too high. could not compensate by increasing duration between path points.'
                raise MinorError(ErrorCodes.e001011, error_message)
            else:
                warning_message = 'acceleration too high. path was saved with longer duration between all points.'
                self.interface.set_message_info(warning_message, 'Warning', 2, 2)
            for i in range(len(data)):
                data[i][1] = duration
        self.arm.context.record_path = [initial_joint_angles, data]
        #return [initial_joint_angles, data]

    def stop(self):
        if self.arm.is_recording:
            self.arm.is_recording = False
        else:
            assertion_message = 'path was not being recorded.'
            raise MinorError(ErrorCodes.e001024, assertion_message)
