'''
@Project: Neocobot

@Created: 23-Oct-2017 by Chen Zhuo

'''
from tkinter import *
from tkinter.ttk import Combobox


class DictCombobox(Combobox):
    def __init__(self, master, dictionary={}, *args, **kw):
        Combobox.__init__(self, master, values=sorted(list(dictionary.keys())), *args, **kw)
        self.dictionary = dictionary

    def set_dict(self, dictionary):
        self.dictionary = dictionary
        self['values'] = sorted(list(dictionary.keys()))

    def value(self):
        return self.dictionary[self.get()]


class FRAME_PROJECT(Frame):

    def __init__(self, controller, master=None):
        Frame.__init__(self, master)
        self.root = master
        self._controller = controller
        self.__init_params__()
        self.__createWidgets__()

    def __init_params__(self):
        _tp = self._controller.get_all_projects()
        self._projects = {p['name']:p['id'] for p in _tp}

    def __createWidgets__(self):
        self.__project_zone__(0)
        self.__pose_zone__(2)
        self.__update_pose_list__()

    def __project_zone__(self, start_row):
        Label(self, text="Select Project:").grid(row=start_row, column=0, pady=12, padx=4, sticky=W)

        self.cb_project = DictCombobox(self, dictionary=self._projects, state='readonly')
        self.cb_project.grid(row=start_row, column=1, columnspan=4)
        self.cb_project.bind("<<ComboboxSelected>>", self.__project_changed__)
        self.cb_project.current(0)

        Label(self, text="Pose:").grid(row=start_row+1, column=0, pady=12)

        self.cb_pose = DictCombobox(self, state='readonly')
        self.cb_pose.grid(row=start_row+1, column=1, columnspan=4)
        self.cb_pose.bind("<<ComboboxSelected>>", self.__display_pose__)

        self.btn_deletepose = Button(self, text="Delete", command=self.__delete_pose__, state=DISABLED)
        self.btn_deletepose.grid(row=start_row+1, column=5, padx=8)

        self.btn_movepose = Button(self, text="Move to", command=self.__move_pose__, state=DISABLED)
        self.btn_movepose.grid(row=start_row + 1, column=6, padx=8)

    def __pose_zone__(self, start_row):
        Label(self, text=" ").grid(row=start_row, column=0, pady=6)

        self.lb_xyz_pos = Label(self, text='Coords', anchor='e')
        self.lb_xyz_pos.grid(row=start_row + 1, column=0, rowspan=2)

        self.lb_x = Label(self, text='X')
        self.lb_x.grid(row=start_row + 1, column=2)

        self.lb_y = Label(self, text='Y')
        self.lb_y.grid(row=start_row + 1, column=3)

        self.lb_z = Label(self, text='Z')
        self.lb_z.grid(row=start_row + 1, column=4)

        self.lb_roll = Label(self, text='Roll')
        self.lb_roll.grid(row=start_row + 1, column=5)

        self.lb_pitch = Label(self, text='Pitch')
        self.lb_pitch.grid(row=start_row + 1, column=6)

        self.lb_yaw = Label(self, text='Yaw')
        self.lb_yaw.grid(row=start_row + 1, column=7)

        self.lb_x_value = Label(self, width=8)
        self.lb_x_value.grid(row=start_row + 2, column=2)

        self.lb_y_value = Label(self, width=8)
        self.lb_y_value.grid(row=start_row + 2, column=3)

        self.lb_z_value = Label(self, width=8)
        self.lb_z_value.grid(row=start_row + 2, column=4)

        self.lb_roll_value = Label(self, width=8)
        self.lb_roll_value.grid(row=start_row + 2, column=5)

        self.lb_pitch_value = Label(self, width=8)
        self.lb_pitch_value.grid(row=start_row + 2, column=6)

        self.lb_yaw_value = Label(self, width=8)
        self.lb_yaw_value.grid(row=start_row + 2, column=7)

        self.lb_blank = Label(self, text='')
        self.lb_blank.grid(row=start_row + 3)

        self.lb_angles_pos = Label(self, text='Angels', anchor='e')
        self.lb_angles_pos.grid(row=start_row + 4, column=0, rowspan=2)

        self.lb_angle = []
        for i in range(6):
            self.lb_angle.append(Label(self, text="Axis " + str(i + 1)))
            self.lb_angle[i].grid(row=start_row + 4, column=i + 2)

        self.lb_angle_value = []
        for i in range(6):
            self.lb_angle_value.append(Label(self, width=8))
            self.lb_angle_value[i].grid(row=start_row + 5, column=i + 2)

    def __project_changed__(self, event):
        _project_id = self.cb_project.value()
        self._controller.switch_project(_project_id)
        self.__update_pose_list__()
        self.cb_pose.set("")
        self.btn_deletepose.config(state=DISABLED)
        self.btn_movepose.config(state=DISABLED)

    def __display_pose__(self, event):
        self.btn_deletepose.config(state=NORMAL)
        self.btn_movepose.config(state=NORMAL)
        id = self.cb_pose.value()
        pose = self._controller.get_pose(id)
        pose_data = pose['pose_data']
        angles = pose['actuator_angles']
        self.__update_posedata__(pose_data, angles)

    def __update_posedata__(self, pose_data=[0]*6, angles=[0]*6):
        self.lb_x_value['text'] = str(pose_data[0])[0:6]
        self.lb_y_value['text'] = str(pose_data[1])[0:6]
        self.lb_z_value['text'] = str(pose_data[2])[0:6]
        self.lb_roll_value['text'] = str(pose_data[3])[0:6]
        self.lb_pitch_value['text'] = str(pose_data[4])[0:6]
        self.lb_yaw_value['text'] = str(pose_data[5])[0:6]

        for i in range(len(angles)):
            self.lb_angle_value[i]['text'] = str(angles[i])[0:6]

    def __update_pose_list__(self):
        _pl = self._controller.get_all_poses()
        self._pose_list = {p['name']:p['id'] for p in _pl}
        self.cb_pose.set_dict(self._pose_list)
        self.__update_posedata__()

    def __delete_pose__(self):
        id = self.cb_pose.value()
        if not(id == ""):
            self._controller.delete_pose(id)
            self.__update_pose_list__()
            self.cb_pose.set("")
            self.btn_deletepose.config(state=DISABLED)
            self.btn_movepose.config(state=DISABLED)

    def __move_pose__(self):
        #id = self.cb_pose.value()
        #self._controller.move_to_pose(id=id)
        name = self.cb_pose.get()
        self._controller.move_to_pose(name)