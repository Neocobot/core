from sys import version_info
if version_info >= (3, 3, 0):
    def swig_import_arm():
        import importlib
        fp = None
        try:
            fp = importlib.import_module('neocobot.model.controller')
        except ImportError:
            import neocobot.model.controller
            return neocobot.model.controller.Controller
        if fp is not None:
            try:
                _mod = fp.Controller
            finally:
                pass
        return _mod
    Controller = swig_import_arm()
    del swig_import_arm

else:
    from neocobot.model.controller import Controller
del version_info


class NeoCobot():
    ARM_CALIBRATION_USE_EXISTING = Controller.ARM_CALIBRATION_USE_EXISTING
    ARM_CALIBRATION_AUTO = Controller.ARM_CALIBRATION_AUTO
    ARM_CALIBRATION_MAX_POSITION = Controller.ARM_CALIBRATION_MAX_POSITION

    def __init__(self):
        self.__controller = Controller()

    def initialize(self, parameters, hand=None):
        return self.__controller.initialize(parameters, hand)

    def is_initialize(self):
        return self.__controller.is_initialize()

    def finalize(self):
        return self.__controller.finalize()

        return self.__controller.calibrate(mode)

    def pause(self):
        return self.__controller.pause()

    def resume(self):
        return self.__controller.resume()

    def stop(self):
        return self.__controller.stop()

    def release(self, actuator_ids=None):
        return self.__controller.release(actuator_ids)

    def hold(self, actuator_ids=None):
        return self.__controller.hold(actuator_ids)

    def reset(self):
        return self.__controller.reset()

    #######################################
    # Script
    #######################################
    '''
    support function:
    :func move_point
    :func set_hand_signal
    :func move_angles
    :func reset
    '''
    def run_script_code(self, script_code, block=True, callback=None):
        return self.__controller.run_script_code(script_code, block=block, callback=callback)

    def run_script(self, script_name, block=True):
        return self.__controller.run_script({'script_name': script_name}, block)

    def save_script(self, script_name, script_code):
        return self.__controller.save_script({'script_name': script_name,
                                              'script_code':script_code})

    #######################################
    # PVT Mode
    #######################################
    '''
    declare a new pvt motion
    '''
    def new_pvt_motion(self):
        return self.__controller.new_pvt_motion()

    '''
    :param points: a list of points that robot arm is expected to reach smoothly in sequence. 
                   format: [[x, y, z, [roll, pitch, yaw]], ]
    :param closed: the route is closed if True
    :linear_segments: 
    '''
    def add_pvt_path(self, points, closed=False, max_velocity=None, max_acceleration=None, linear_segments=None):
        return self.__controller.add_pvt_path(points, closed, max_velocity, max_acceleration, linear_segments)

    def pvt_move(self):
        return self.__controller.pvt_move()

    def save_pvt(self, pvt_name):
        return self.__controller.save_pvt(pvt_name)

    def load_pvt(self, pvt_name):
        return self.__controller.load_pvt(pvt_name)

    def set_pvt_points(self, pvt_points):
        return self.__controller.set_pvt(pvt_points)

    #######################################
    # Pose
    #######################################
    def save_pose(self, pose_name, angles=None):
        if angles is None:
            return self.__controller.save_pose({'pose_name': pose_name})
        else:
            return self.__controller.save_pose({'pose_name': pose_name, 'actuator_angles':angles})

    def move_to_pose(self, name, velocity=None, acceleration=None, block=True):
        return self.__controller.move_to_pose({'pose_name': name}, velocity, acceleration, block)

    def get_pose(self, id):
        return self.__controller.get_pose(id)

    def get_all_poses(self):
        return self.__controller.get_all_pose()

    def delete_pose(self, id):
        return self.__controller.delete_pose(id)

    #######################################
    # Status
    #######################################
    '''
    :return position = [angles]
    '''
    def get_position(self, actuator_ids=None):
        return self.__controller.get_present_position(actuator_ids)

    '''
    :return posture = [x, y, z, orientation=[roll, pitch, yaw]]
    '''
    def get_posture(self):
        return self.__controller.get_posture()

    def get_released_status(self):
        status = self.__controller.get_released_status()
        return status

    #######################################
    # Move
    #######################################
    '''
    :param x, y, z: describe the space coordinate at the end of robot arm
    :param orientation: [roll, pitch, yaw] describe the orientation of the hand
    :param relative: flag on whether this is a relative motion
    :sample move_point(0, 250, 600, orientation=[180, 0, -90], block=True)
    :sample move_point(50, 50, 0, relative=True)
    '''
    def move_point(self, x, y, z, orientation=None, block=True, velocity=None, acceleration=None, relative=False):
        return self.__controller.move_point(x, y, z, orientation, relative, block, velocity, acceleration)

    '''
    :param angles: [angle1, angle2, angle3, ...]
    :sample move_angles([30, 40, 60, -40, 0, 90], relative=False): move to angles[30, 40, 60, -40, 0, 90]
    :sample move_angles([0, 0, 50, 0, 0, -60], relative=True): move an offset[0, 0, 50, 0, 0, -60]
    '''
    def move_angles(self, angles, block=True, velocity=None, acceleration=None, relative=False):
        return self.__controller.move_angles(angles, block, velocity, acceleration, relative)

    '''
    :param actuator_ids: the actuator ids that are to be included in the motion. e.g.=[1, 3, 4, 5]
    :param angles: angles by which the actuators will move measured in [degrees]
    '''
    def move_joint(self, actuator_ids, angles, velocity=None, acceleration=None, block=True, relative=False):
        return self.__controller.move_joint(actuator_ids, angles, velocity, acceleration, block, relative)

    '''
    :param signal: string = 'open' or 'close'   e.g. set_hand_signal('open')
    '''
    def set_hand_signal(self, signal):
        return self.__controller.set_hand_signal(signal)

    #######################################
    # Project
    #######################################
    def get_all_projects(self):
        return self.__controller.get_all_projects()

    def switch_project(self, id):
        return self.__controller.change_project(id)

    def save_project(self, name, id=0):
        return self.__controller.save_project(name, id)

    #######################################
    # Others
    #######################################
    def wait(self, wait_time):
        return self.__controller.wait(wait_time)

    def get_angles_limit(self, actuator_id=None):
        return self.__controller.get_angles_limit(actuator_id)







