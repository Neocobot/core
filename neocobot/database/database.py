'''
@Project: Neocobot

@Created: 06-June-2017 by Chen Zhuo

This file includes all the functions that load and save data from and in the database.
'''
import inspect
import json
import os
import sqlite3
import time

from neocobot.error.error import RobotError, DatabaseError
from neocobot.log.log import Log, DatabaseLog

from neocobot.error.error_code import ErrorCodes


def _handle_database(func):
    '''
    This is a decorator function to open a database file, save any changes, and close the file.
    The function wrapped by this decorator can not be a static function.
    It prepares self.connection and self.cursor for the use of the wrapped function.
    :param func: wrapped function
    :return: returned value of the wrapped function
    '''

    def _wrapped_func(*args, **kargs):
        _self = args[0]
        if _self.table.database.connection_number == 0:
            _self.table.database.connection = sqlite3.connect(_self.table.database.file_path)
            _self.table.database.cursor = _self.table.database.connection.cursor()
        _self.table.database.connection_number += 1
        try:
            ans = func(*args, **kargs)
        except sqlite3.OperationalError:
            error_message = 'your version of the database is no longer supported.'
            raise DatabaseError(ErrorCodes.e002001, error_message)
        except sqlite3.ProgrammingError:
            error_message = 'succession of commands was too fast for database.'
            raise DatabaseError(ErrorCodes.e002002, error_message)
        except RobotError as error:
            raise error
            
        else:
            _self.table.database.connection.commit()
        finally:
            _self.table.database.connection_number -= 1
            if _self.table.database.connection_number == 0:
                _self.table.database.connection.close()
                _self.table.database.connection = None
                _self.table.database.cursor = None
        return ans

    return _wrapped_func


class Database:
    __qualname__ = 'Database'

    def __init__(self, file_name):
        folder_path = os.path.abspath(os.path.dirname(inspect.stack()[0][1]))
        file_path = os.path.normpath(os.path.join(folder_path, file_name))
        self.file_path = file_path
        self.connection = None
        self.cursor = None
        self.connection_number = 0


class RobotDatabase(Database):
    __qualname__ = 'RobotDatabase'

    def __init__(self, file_name):
        Database.__init__(self, file_name)
        self.projects = Projects(self)
        self.info = Info(self)
        self.scripts = Scripts(self, self.projects)
        self.poses = Poses(self, self.projects)
        self.paths = Paths(self, self.projects)
        self.pvt = PVT(self, self.projects)
        self.pose_database = PoseDatabase(self)
        if len(self.projects.get()) == 0:
            elements = self.projects.create_elements_field()
            self.projects.add(name='Default', elements=elements)

class Table:
    __qualname__ = 'Table'

    class Get:
        __qualname__ = 'Table.Get'

        def __init__(self, table):
            self.element_id = None
            self.table = table
            self.columns = []
            self.elements = []

        @_handle_database
        def __call__(self, *args, **kargs):
            '''
            retrieve an element from the database.
            :param element_id: id of the element. if id is None, all elements are retrieved.
            :return: [id, name, joint_angles]
            :rtype: dict or list
            '''
            self.prepare_arguments(*args)
            self.create_sql_and_execute(**kargs)
            self.prepare_elements()
            return self.elements

        def prepare_arguments(self, *args):
            self.__init__(self.table)
            if len(args) == 0:
                self.columns = self.table.columns.copy()
            else:
                if type(args[0]) is int:
                    self.element_id = str(args[0])
                    if len(args) == 1:
                        self.columns = self.table.columns.copy()
                    else:
                        self.columns = list(args)[1:]
                else:
                    self.columns = list(args)
            for column in self.columns:
                if column not in self.table.columns:
                    assertion_message = 'a column "' + column + '" does not exist in table "' + self.table.table_name + '".'
                    raise DatabaseError(ErrorCodes.e002003, assertion_message)

        def create_sql_and_execute(self, **kargs):
            self.table.database.connection.commit()
            sql_string = 'SELECT '
            sql_string += ', '.join(self.columns)
            sql_string += ' FROM ' + self.table.table_name
            if self.element_id is None:
                if len(kargs) > 0:
                    column_values = kargs.copy()
                    for (key, value) in column_values.items():
                        column_values[key] = '\"' + value + '\"'
                    sql_string += ' WHERE '
                    sql_string += ' AND '.join([key + '=:' + key for (key, _) in column_values.items()])
                    self.table.database.cursor.execute(sql_string, column_values)
                else:
                    self.table.database.cursor.execute(sql_string)
            else:
                sql_string += ' WHERE id=:id'
                self.table.database.cursor.execute(sql_string, {'id': self.element_id})

        def prepare_elements(self):
            element_data = self.table.database.cursor.fetchall()
            for i in range(len(element_data)):
                self.elements.append(dict(zip(self.columns, list(element_data[i]))))
            for column in self.columns:
                if self.table.column_types[column] == 'TEXT':
                    for i in range(len(self.elements)):
                        try:
                            self.elements[i][column] = None if self.elements[i][column] is None else json.loads(self.elements[i][column])
                        except ValueError:
                            error_message = 'your version of the database is no longer supported.'
                            raise DatabaseError(ErrorCodes.e002004, error_message)
            if self.element_id is not None:
                if len(self.elements) == 0:
                    error_message = "id \""+str(self.element_id)+"\" does not exist in \""+self.table.table_name+"\"."
                    raise DatabaseError(ErrorCodes.e002005, error_message)
                self.elements = self.elements[0]

    class Add:
        __qualname__ = 'Table.Add'

        def __init__(self, table):
            self.table = table
            self.column_values = {}
            self.current_elements = []

        @_handle_database
        def __call__(self, **kwargs):
            '''
            add a element to the database.
            :param name: name of the element.
            :param joint_angles: list of floats representing the angles of each kinematic joint.
            :return: id of last created entry
            '''
            self.prepare_arguments(**kwargs)
            self.check_overwrite()
            self.create_sql_and_execute()

        def prepare_arguments(self, **kwargs):
            self.__init__(self.table)
            self.column_values = kwargs.copy()
            self.column_values['created'] = time.strftime('%Y-%m-%d %H:%M')
            self.column_values['modified'] = time.strftime('%Y-%m-%d %H:%M')
            if len(self.column_values) != len(self.table.columns) - 1:
                assertion_message = 'all columns except id must be defined in order to add an element.'
                raise DatabaseError(ErrorCodes.e002006, assertion_message)
            for column_name in self.column_values:
                if column_name not in self.table.columns:
                    assertion_message = 'a column "' + column_name + '" does not exist.'
                    raise DatabaseError(ErrorCodes.e002007, assertion_message)
            self.current_elements = self.table.get('id', 'name')

        def check_overwrite(self):
            existing_id = self.table.get_id_from_name(self.column_values['name'], self.current_elements)
            if existing_id > 0:
                self.table.delete(existing_id)

        def create_sql_and_execute(self):
            for column_name in self.column_values:
                if self.table.column_types[column_name] == 'TEXT':
                    self.column_values[column_name] = json.dumps(self.column_values[column_name])
            sql_string = 'INSERT INTO ' + self.table.table_name + ' VALUES (NULL, :'
            sql_string += ', :'.join(self.table.get_ordered_column_list(self.column_values))
            sql_string += ')'
            self.table.database.cursor.execute(sql_string, self.column_values)
            created_element = self.table.get()[-1]
            DatabaseLog.write(Log.INFO, 'Database Add (' + self.table.table_name + '): ' + str(created_element))

    class Edit:
        __qualname__ = 'Table.Edit'

        def __init__(self, table):
            self.table = table
            self.column_values = {}
            self.current_elements = []
            self.element_id = 0

        @_handle_database
        def __call__(self, element_id, **kwargs):
            '''
            edit a element of the database.
            :param element_id: id of the element
            :param name: name of the element
            :param joint_angles: list of floats representing the angles of each kinematic joint.
            '''
            self.prepare_arguments(element_id, **kwargs)
            self.check_for_existing()
            self.create_sql_and_execute()

        def prepare_arguments(self, element_id, **kwargs):
            self.__init__(self.table)
            self.column_values = kwargs.copy()
            if len(self.column_values) == 0:
                assertion_message = 'at least one column needs to be changed.'
                raise DatabaseError(ErrorCodes.e002008, assertion_message)
            self.column_values['modified'] = time.strftime('%Y-%m-%d %H:%M')
            for column_name in self.column_values:
                if column_name not in self.table.columns:
                    assertion_message = 'a column "' + column_name + '" does not exist.'
                    raise DatabaseError(ErrorCodes.e002009, assertion_message)
            self.element_id = element_id
            self.current_elements = self.table.get('id', 'name')

        def check_for_existing(self):
            if 'name' in self.column_values:
                existing_id = self.table.get_id_from_name(self.column_values['name'], self.current_elements)
                if existing_id > 0 and existing_id != self.element_id:
                    error_message = 'the name that you chose already exists.'
                    raise DatabaseError(ErrorCodes.e002010, error_message)

        def create_sql_and_execute(self):
            for column_name in self.column_values:
                if self.table.column_types[column_name] == 'TEXT':
                    self.column_values[column_name] = json.dumps(self.column_values[column_name])
            origin_element = self.table.get(self.element_id)
            ordered_column_list = self.table.get_ordered_column_list(self.column_values)
            sql_string = 'UPDATE ' + self.table.table_name + ' SET '
            sql_string += ', '.join([i + '=:' + j for (i, j) in zip(ordered_column_list, ordered_column_list)])
            sql_string += ' WHERE id=:id'
            self.column_values['id'] = self.element_id
            self.table.database.cursor.execute(sql_string, self.column_values)
            edited_element = self.table.get(self.element_id)
            DatabaseLog.write(Log.INFO, 'Database Delete (' + self.table.table_name + "): " + str(origin_element) + " to " + str(edited_element))

    class Delete:
        __qualname__ = 'Table.Delete'

        def __init__(self, table):
            self.table = table
            self.element_id = 0

        @_handle_database
        def __call__(self, element_id):
            '''
            delete a element of the database.
            :param element_id: id of the element
            '''
            self.prepare_arguments(element_id)
            self.create_sql_and_execute()

        def prepare_arguments(self, element_id):
            self.__init__(self.table)
            self.table.get(element_id)
            self.element_id = element_id

        def create_sql_and_execute(self):
            sql_string = 'DELETE FROM ' + self.table.table_name + ' WHERE id=:id'
            delete_element = self.table.get(self.element_id)
            self.table.database.cursor.execute(sql_string, {'id': self.element_id})
            DatabaseLog.write(Log.INFO, 'Database Delete (' + self.table.table_name + "): " + str(delete_element))

    class CreateTable:
        __qualname__ = 'Table.CreateTable'

        def __init__(self, table):
            self.table = table

        @_handle_database
        def __call__(self):
            '''
            delete a element of the database.
            :param element_id: id of the element
            '''
            self.prepare_arguments()
            self.create_sql_and_execute()

        def prepare_arguments(self):
            if 'id' in self.table.columns or 'name' in self.table.columns or 'modified' in self.table.columns or 'created' in self.table.columns:
                assertion_message = 'columns "id", "name", "modified" and "created" are reserved.'
                raise DatabaseError(ErrorCodes.e002011, assertion_message)
            self.table.columns = ['id', 'name'] + self.table.columns + ['modified', 'created']
            self.table.column_types['id'] = 'INTEGER PRIMARY KEY'
            self.table.column_types['name'] = 'TEXT'
            self.table.column_types['modified'] = 'TEXT'
            self.table.column_types['created'] = 'TEXT'
            for column in self.table.columns:
                if column not in self.table.column_types:
                    assertion_message = 'no column type for column "' + column + '".'
                    raise DatabaseError(ErrorCodes.e002012, assertion_message)

        def create_sql_and_execute(self):
            column_type_list = []
            for column in self.table.columns:
                column_type_list.append(self.table.column_types[column])
            sql_string = 'CREATE TABLE IF NOT EXISTS ' + self.table.table_name + ' ('
            sql_string += ', '.join([i + ' ' + j for (i, j) in zip(self.table.columns, column_type_list)])
            sql_string += ')'
            self.table.database.cursor.execute(sql_string)
            DatabaseLog.write(Log.INFO, 'Database Create Table: ' + self.table.table_name + "(" + str(self.table.columns) + ")")

    def __init__(self, database, table_name, columns, column_types):
        self.database = database
        self.table_name = table_name
        self.columns = columns
        self.column_types = column_types
        self.get = self.Get(self)
        self.add = self.Add(self)
        self.edit = self.Edit(self)
        self.delete = self.Delete(self)
        self.create_table = self.CreateTable(self)
        self.create_table()

    def get_id_from_name(self, name, elements=None):
        '''
        return the id of a pose with a certain name.
        :param name: name of the pose.
        :return: id of the pose. if the pose name does not exist, pose id is 0.
        '''
        if elements is None:
            elements = self.get()
        element_id = 0
        for element in elements:
            name_slug = name.replace(' ', '_')
            element_slug = element['name'].replace(' ', '_')
            if name_slug.lower() == element_slug.lower():
                element_id = element['id']
                break
        return element_id

    def get_ordered_column_list(self, columns):
        column_list = []
        for column in self.columns:
            if column in columns:
                column_list.append(column)
        return column_list

    def get_crucial_elements(self, *args):
        elements = self.get(*args)
        return elements


class ProjectTable(Table):
    __qualname__ = 'ProjectTable'

    class Add(Table.Add):
        __qualname__ = 'ProjectTable.Add'

        def __init__(self, table):
            Table.Add.__init__(self, table)
            self.project_id = 1

        @_handle_database
        def __call__(self, **kwargs):
            '''
            add a element to the database.
            :param name: name of the element.
            :param joint_angles: list of floats representing the angles of each kinematic joint.
            :return: id of last created entry
            '''
            self.prepare_arguments(project_id=self.project_id, **kwargs)
            self.check_overwrite()
            self.create_sql_and_execute()
            self.add_to_project()

        def prepare_arguments(self, project_id, **kwargs):
            Table.Add.prepare_arguments(self, **kwargs)
            self.project_id = project_id
            self.current_elements = self.table.get_crucial_elements(self.project_id, 'id', 'name')

        def add_to_project(self):
            element_id = self.table.get('id')[-1]['id']
            self.table.projects.add_element(self.project_id, element_id, self.table.table_name)

    class Edit(Table.Edit):
        __qualname__ = 'ProjectTable.Edit'

        def __init__(self, table):
            Table.Edit.__init__(self, table)

        def prepare_arguments(self, element_id, **kwargs):
            Table.Edit.prepare_arguments(self, element_id, **kwargs)
            projects = self.table.database.projects.get('id', 'elements')
            for project in projects:
                if element_id in project['elements'][self.table.table_name]:
                    project_id = project['id']
                    break
                else:
                    assertion_message = 'element with id "' + str(element_id) + '" does not belong to a project.'
                    raise DatabaseError(ErrorCodes.e002013, assertion_message)
            self.current_elements = self.table.get_crucial_elements(project_id, 'id', 'name')

    class Delete(Table.Delete):
        __qualname__ = 'ProjectTable.Delete'

        def __init__(self, table):
            Table.Delete.__init__(self, table)

        @_handle_database
        def __call__(self, element_id):
            '''
            delete a element of the database.
            :param element_id: id of the element
            '''
            self.prepare_arguments(element_id)
            self.delete_from_project()
            self.create_sql_and_execute()

        def delete_from_project(self):
            self.table.projects.delete_element(self.element_id, self.table.table_name)

    class CreateTable(Table.CreateTable):
        __qualname__ = 'ProjectTable.CreateTable'

        def __init__(self, table):
            Table.CreateTable.__init__(self, table)

        @_handle_database
        def __call__(self):
            '''
            delete a element of the database.
            :param element_id: id of the element
            '''
            self.prepare_arguments()
            self.create_sql_and_execute()
            self.add_to_project_tables()

        def add_to_project_tables(self):
            self.table.projects.project_tables[self.table.table_name] = self.table

    def __init__(self, database, projects, table_name, columns, column_types):
        self.projects = projects
        Table.__init__(self, database, table_name, columns, column_types)

    def get_id_from_name(self, name, elements, project_id=None):
        '''
        return the id of a pose with a certain name.
        :param name: name of the pose.
        :return: id of the pose. if the pose name does not exist, pose id is 0.
        '''
        if elements is None:
            elements = self.get_crucial_elements(project_id)
        return Table.get_id_from_name(self, name, elements)

    def get_crucial_elements(self, project_id, *args):
        elements = self.get(*args)
        current_project = self.projects.get(project_id)
        crucial_elements = []
        for element in elements:
            if element['id'] in current_project['elements'][self.table_name]:
                crucial_elements.append(element)
        return crucial_elements


class Projects(Table):
    __qualname__ = 'Projects'

    class Delete(Table.Delete):
        __qualname__ = 'Projects.Delete'

        def __init__(self, table):
            Table.Delete.__init__(self, table)
            self.current_project = {}

        @_handle_database
        def __call__(self, element_id):
            '''
            delete a element of the database.
            :param element_id: id of the element
            '''
            self.prepare_arguments(element_id)
            self.delete_containing_elements()
            self.create_sql_and_execute()

        def prepare_arguments(self, element_id):
            self.__init__(self.table)
            if element_id == 1:
                assertion_message = 'The default project cannot be deleted.'
                raise DatabaseError(ErrorCodes.e002014, assertion_message)
            self.current_project = self.table.get(element_id)
            self.element_id = element_id

        def delete_containing_elements(self):
            for table in self.table.project_tables:
                for element_id in self.current_project['elements'][table]:
                    self.table.project_tables[table].delete(element_id)

    def __init__(self, database):
        table_name = 'projects'
        columns = ['elements']
        column_types = {'elements': 'TEXT'}
        Table.__init__(self, database, table_name, columns, column_types)
        self.project_tables = {}

    def add_element(self, project_id, element_id, table_name):
        current_project = self.get(project_id, 'elements')
        elements = current_project['elements']
        if element_id not in elements[table_name]:
            elements[table_name].append(element_id)
        self.edit(project_id, elements=elements)

    def delete_element(self, element_id, table_name):
        projects = self.get('id', 'elements')
        for project in projects:
            if element_id in project['elements'][table_name]:
                project['elements'][table_name].remove(element_id)
                self.edit(project['id'], elements=project['elements'])
                break
            else:
                assertion_message = 'element with id "' + str(element_id) + '" does not exist in "' + table_name + '".'
                raise DatabaseError(ErrorCodes.e002015, assertion_message)

    def move_element(self, project_id, element_id, element_table, make_copy):
        for project in self.get():
            if element_id in project['elements'][element_table]:
                from_project = project
                break
            else:
                assertion_message = 'element with id "' + str(element_id) + '" does not exist in "' + element_table + '".'
                raise DatabaseError(ErrorCodes.e002016, assertion_message)
        to_project = self.get(project_id)
        current_element = self.project_tables[element_table].get(element_id)
        if to_project['id'] == from_project['id']:
            error_message = 'cannot move element within the same project.'
            raise DatabaseError(ErrorCodes.e002017, error_message)
        if make_copy:
            del current_element['id']
            self.project_tables[element_table].add(project_id=project_id, **current_element)
        else:
            to_elements = self.project_tables[element_table].get_crucial_elements(project_id=project_id)
            for this_element in to_elements:
                if this_element['name'] == current_element['name']:
                    self.project_tables[element_table].delete(this_element['id'])
                    to_project = self.get(project_id)
            new_elements = from_project['elements']
            new_elements[element_table].remove(element_id)
            self.edit(from_project['id'], elements=new_elements)
            new_elements = to_project['elements']
            new_elements[element_table].append(element_id)
            self.edit(to_project['id'], elements=new_elements)

    def create_elements_field(self):
        elements = {}
        for table in self.project_tables:
            elements[table] = []
        return elements


class Scripts(ProjectTable):
    __qualname__ = 'Scripts'

    def __init__(self, database, projects):
        table_name = 'scripts'
        columns = ['code']
        column_types = {'code': 'TEXT'}
        ProjectTable.__init__(self, database, projects, table_name, columns, column_types)


class Poses(ProjectTable):
    __qualname__ = 'Poses'

    def __init__(self, database, projects):
        table_name = 'poses'
        columns = ['pose_data', 'actuator_angles']
        column_types = {'pose_data': 'TEXT', 'actuator_angles': 'TEXT'}
        ProjectTable.__init__(self, database, projects, table_name, columns, column_types)


class Paths(ProjectTable):
    __qualname__ = 'Paths'

    def __init__(self, database, projects):
        table_name = 'paths'
        columns = ['initial_actuator_angles', 'pt_points']
        column_types = {'initial_actuator_angles': 'TEXT', 'pt_points': 'TEXT'}
        ProjectTable.__init__(self, database, projects, table_name, columns, column_types)


class PVT(ProjectTable):
    __qualname__ = 'PVT'

    def __init__(self, database, projects):
        table_name = 'pvt'
        columns = ['pvt_data']
        column_types = {'pvt_data': 'TEXT'}
        ProjectTable.__init__(self, database, projects, table_name, columns, column_types)


class Info(Table):
    __qualname__ = 'Info'

    def __init__(self, database):
        table_name = 'info'
        columns = ['series', 'type', 'version']
        column_types = {'series': 'TEXT', 'type': 'TEXT', 'version': 'TEXT'}
        Table.__init__(self, database, table_name, columns, column_types)
        self.project_tables = {}

    def is_empty(self):
        if len(self.get()) > 0:
            return False
        return True

    def erase_table(self):
        self.table.database.cursor.execute('DELETE FROM ' + self.table.table_name + ' WHERE 1=1', self.column_values)


class PoseDatabase:
    __qualname__ = 'PoseDatabase'

    def __init__(self, database):
        self.database = database

    def get_pose_from_database(self, pose_name):
        '''Get a pose from the database.

        :param pose_name:
        :return:
        '''
        if type(pose_name) is str:
            pose_id = self.database.poses.get_id_from_name(pose_name)
            error_message = 'The specified pose name ' + pose_name + ' does not exist.'
            raise DatabaseError(ErrorCodes.e002018, error_message)
        else:
            pose_id = pose_name
        pose_data = self.database.poses.get(pose_id)['pose_data']
        actuator_data = self.database.poses.get(pose_id)['actuator_angles']
        return (pose_data[:3], actuator_data)
