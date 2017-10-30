'''
@Project: Neocobot

@Created: 06-June-2017 by Chen Zhuo
'''
import inspect
import json
import os

from neocobot.error.error import MinorError, DatabaseError
from neocobot.error.error_code import ErrorCodes

from neocobot.database.database import RobotDatabase


class Dao:
    __qualname__ = "Dao"

    def __init__(self, arm):
        self.arm = arm
        self.database = RobotDatabase('neocobot.db')
        self.init_info()


###################### Project #####################
    def project_name_duplicated(self, project_name):
        project_name_list = self.database.projects.get('name', name=project_name)
        #project_ids = self.database.projects.get_id_from_name(project_name)
        return {'name': project_name} in project_name_list

    def save_project(self, arguments):
        if 'project_id' not in arguments:
            error_message = "the argument \'project_id\' is required"
            raise MinorError(ErrorCodes.e001025, error_message)

        if 'project_name' not in arguments:
            error_message = "the argument \'project_name\' is required"
            raise MinorError(ErrorCodes.e001026, error_message)

        project_id = arguments['project_id']
        project_name = arguments['project_name']
        if project_id > 0:
            self.database.projects.edit(project_id,
                                        name=project_name)
        else:
            elements=self.database.projects.create_elements_field()
            self.database.projects.add(name=project_name,
                                       elements=elements)
        return self.get_project({"project_name":project_name})

    def get_project(self, arguments):
        if 'project_id' in arguments:
            project_id = arguments['project_id']
            return self.database.projects.get(project_id)
        elif 'project_name' in arguments:
            project_name = arguments['project_name']
            project_id = self.database.projects.get_id_from_name(project_name)
            return self.database.projects.get(project_id)
        else:
            return self.database.projects.get()

    def delete_project(self, arguments):

        if 'project_id' in arguments:
            project_id = arguments['project_id']
            self.database.projects.delete(project_id)
        else:
            error_message = "the argument \'project_id\' is required"
            raise MinorError(ErrorCodes.e001027, error_message)

    def get_all_projects(self):
        return self.database.projects.get()

####################### Script ######################
    def get_script(self, arguments):
        if 'script_id' not in arguments:
            error_message = "the argument \'script_id\' is required"
            raise MinorError(ErrorCodes.e001028, error_message)

        script_id = arguments['script_id']
        script = self.database.scripts.get(script_id)
        return script

    def get_script_from_name(self, arguments):
        if 'script_name' not in arguments:
            error_message = "the argument \'script_name\' is required"
            raise MinorError(ErrorCodes.e001029, error_message)

        script_name = arguments['script_name']
        return self.database.scripts.get_id_from_name(script_name, self.arm.project['id'])

    def get_all_scripts(self):
        scripts = self.database.scripts.get_crucial_elements(self.arm.project['id'])
        return scripts

    def save_script(self, arguments):
        if 'script_name' not in arguments:
            error_message = "the argument \'script_name\' is required"
            raise MinorError(ErrorCodes.e001030, error_message)
        if 'script_code' not in arguments:
            error_message = "the argument \'script_code\' is required"
            raise MinorError(ErrorCodes.e001031, error_message)

        script_name = arguments['script_name']
        script_code = arguments['script_code']
        script_id = self.database.scripts.get_id_from_name(script_name, self.arm.project['id'])
        if script_id > 0:
            self.database.scripts.edit(script_id,
                                       code=script_code)
        else:
            self.database.scripts.add(name=script_name,
                                      code=script_code)
        arguments = {'script_id': script_id}
        return self.get_script(arguments)

    def delete_script(self, arguments):
        if 'script_id' not in arguments:
            error_message = "the argument \'script_id\' is required"
            raise MinorError(ErrorCodes.e001032, error_message)

        script_id = arguments['script_id']
        self.database.scripts.delete(script_id)

####################### Pose ########################
    def get_poseid_from_name(self, arguments):
        if 'pose_name' not in arguments:
            error_message = "the argument \'pose_name\' is required"
            raise MinorError(ErrorCodes.e001033, error_message)

        pose_name = arguments["pose_name"]
        return self.database.poses.get_id_from_name(pose_name, None, self.arm.project['id'])

    def get_pose(self, arguments):
        if 'pose_id' not in arguments:
            error_message = "the argument \'pose_id\' is required"
            raise MinorError(ErrorCodes.e001034, error_message)

        pose_id = arguments["pose_id"]
        return self.database.poses.get(pose_id)

    def get_all_poses(self):
        return self.database.poses.get_crucial_elements(self.arm.project['id'])

    def save_pose(self, arguments):
        if 'pose_name' not in arguments:
            error_message = "the argument \'pose_name\' is required"
            raise MinorError(ErrorCodes.e001035, error_message)

        pose_name = arguments['pose_name']

        actuator_ids = self.arm.config.get_kinematic_indices()
        actuator_angles = []
        if 'actuator_angles' in arguments:
            actuator_angles = arguments['actuator_angles']
            if not (len(actuator_ids) == len(actuator_ids)):
                actuator_angles = self.arm.get_position(actuator_ids)
        else:
            actuator_angles = self.arm.get_position(actuator_ids)
        pose_data = self.arm.kinematics.convert_joint_angles_to_pose(actuator_angles)
        self.database.poses.add(name=pose_name,
                                pose_data=pose_data,
                                actuator_angles=actuator_angles)

    def delete_pose(self, arguments):
        if 'pose_id' not in arguments:
            error_message = "the argument \'pose_id\' is required"
            raise MinorError(ErrorCodes.e001036, error_message)

        pose_id = arguments['pose_id']
        self.database.poses.delete(pose_id)


####################### PVT #########################
    def save_PVT(self, arguments):
        if 'pvt_name' not in arguments:
            error_message = "the argument \'pvt_name\' is required"
            raise MinorError(ErrorCodes.e001035, error_message)

        pvt_name = arguments['pvt_name']

        if 'pvt_data' not in arguments:
            error_message = "the argument \'pvt_data\' is required"
            raise MinorError(ErrorCodes.e001153, error_message)

        pvt_data = arguments['pvt_data']

        pvt_id = self.database.pvt.get_id_from_name(pvt_name, None, project_id=self.arm.project['id'])

        if pvt_id > 0:
            self.database.pvt.edit(pvt_id, pvt_data=pvt_data)
        else:
            self.database.pvt.add(name=pvt_name,
                              pvt_data=pvt_data)

    def get_pvt_from_name(self, arguments):
        if 'pvt_name' not in arguments:
            error_message = "the argument \'pvt_name\' is required"
            raise MinorError(ErrorCodes.e001033, error_message)

        pvt_name = arguments["pvt_name"]
        id = self.database.pvt.get_id_from_name(pvt_name, None, project_id=self.arm.project['id'])
        return self.database.pvt.get(id)

    def get_pvt(self, arguments):
        if 'pvt_id' not in arguments:
            error_message = "the argument \'pvt_id\' is required"
            raise MinorError(ErrorCodes.e001034, error_message)

            pvt_id = arguments["pvt_id"]
        return self.database.pvt.get(pvt_id)


####################### Path ########################
    def get_path(self, arguments):
        if 'path_id' not in arguments:
            error_message = "the argument \'path_id\' is required"
            raise MinorError(ErrorCodes.e001037, error_message)

        path_id = arguments["path_id"]
        return self.database.paths.get(path_id)

    def get_all_path(self):
        list = self.database.paths.get_crucial_elements(self.arm.project['id'])
        return list

    def get_pathid_from_name(self, arguments):
        if 'path_name' not in arguments:
            error_message = "the argument \'path_name\' is required"
            raise MinorError(ErrorCodes.e001038, error_message)

        path_name = arguments["path_name"]
        return self.database.paths.get_id_from_name(path_name, self.arm.project['id'])

    def add_path(self, arguments):
        if 'path_name' not in arguments:
            error_message = "the argument \'path_name\' is required"
            raise MinorError(ErrorCodes.e001039, error_message)


        if 'pt_points' not in arguments:
            error_message = "the argument \'pt_points\' is required"
            raise MinorError(ErrorCodes.e001040, error_message)

        path_name = arguments['path_name']
        pt_points = arguments['pt_points']
        initial_actuator_angles = arguments['initial_actuator_angles']
        self.database.paths.add(name=path_name,
                                initial_actuator_angles=initial_actuator_angles,
                                pt_points=pt_points)
        return self.get_pathid_from_name({"path_name": path_name})

    def delete_path(self, arguments):
        if 'path_id' not in arguments:
            error_message = "the argument \'path_id\' is required"
            raise MinorError(ErrorCodes.e001041, error_message)

        path_id = arguments["path_id"]
        self.database.paths.delete(path_id)


########################Info##########################
    def _insert_info(self, arguments):
        if 'series' not in arguments:
            error_message = "the argument \'series\' is required"
            raise MinorError(ErrorCodes.e001042, error_message)

        if 'name' not in arguments:
            error_message = "the argument \'name\' is required"
            raise MinorError(ErrorCodes.e001043, error_message)

        if 'type' not in arguments:
            error_message = "the argument \'type\' is required"
            raise MinorError(ErrorCodes.e001044, error_message)

        if 'version' not in arguments:
            error_message = "the argument \'version\' is required"
            raise MinorError(ErrorCodes.e001045, error_message)

        series = arguments['series']
        name = arguments['name']
        arm_type = arguments['type']
        version = arguments['version']
        self.database.info.add(series=series, name=name, type=arm_type, version=version)

    def init_info(self):
        size = len(self.database.info.get())
        if size == 1:
            pass
        else:
            folder_path = os.path.abspath(os.path.dirname(inspect.stack()[0][1]))
            log_path = os.path.normpath(os.path.join(folder_path, "information.conf"))

            try:
                with open(log_path) as json_file:
                    arguments = json.load(json_file)
                    if size == 0:
                        self._insert_info(arguments)
                    elif size > 1:
                        self.database.info.erase_table()
                        self._insert_info(arguments)
            except IOError as e:
                error_message = str(e)
                raise MinorError(ErrorCodes.e001046, error_message)

    def modify_name(self, arguments):
        if 'name' not in arguments:
            error_message = "the argument \'name\' is required"
            raise MinorError(ErrorCodes.e001047, error_message)

        name = arguments['name']
        size = len(self.database.info.get())
        if size == 1:
            id = (self.database.info.get())[0]['id']
            self.database.info.edit(id, name=name)
        elif size > 1:
            info = (self.database.info.get())[-1]
            self.database.info.erase_table()
            info['name'] = name
            self._insert_info(info)
        else:
            error_message = "Arm info is missing"
            raise DatabaseError(ErrorCodes.e002019, error_message)

    def fetch_info(self):
        size = len(self.database.info.get())
        if size == 1:
            info = (self.database.info.get())[0]
            return info
        elif size > 1:
            info = (self.database.info.get())[-1]
            self.database.info.erase_table()
            self._insert_info(info)
            return (self.database.info.get())[0]
        else:
            error_message = "Arm info is missing"
            raise DatabaseError(ErrorCodes.e002020, error_message)
