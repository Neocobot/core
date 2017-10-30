'''
@Project: Neocobot

@Created: 23-Oct-2017 by Chen Zhuo

'''
import threading
import time
from tkinter import *
from tkinter.ttk import Combobox


class StatusListener(threading.Thread):
    INTERVAL = 0.5

    def __init__(self, controller):
        threading.Thread.__init__(self)
        self._controller = controller
        self._running = True
        self._callback = None
        self._enabled = True

    def set_update_callback(self, callback):
        self._callback = callback

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def run(self):
        while self._running:
            position = self._controller.get_position()
            coords = self._controller.get_posture()
            if self._callback is not None and self._enabled:
                self._callback(position, coords)
            time.sleep(self.INTERVAL)

    def stop(self):
        self._running = False


class FRAME_CONTROL(Frame):
    _onMotion = False
    _CALI_TYPE = ['Normal', 'Auto', 'Max Position']
    _CALI_VALUE = dict(zip(_CALI_TYPE, [0, 1, 2]))

    def __init__(self, controller, master=None):
        Frame.__init__(self, master)
        self.root = master
        self._controller = controller
        self.__init_params__()
        try:
            self._angles_limit = self._controller.get_angles_limit()
            self.__update_hold_status__()
        except Exception:
            pass
        self.__createWidgets__()
        self.__init_listener__()

    def __init_params__(self):
        self._velocity = StringVar()
        self._velocity.set("10")

        self._move_x = StringVar()
        self._move_x.set("0")

        self._move_y = StringVar()
        self._move_y.set("0")

        self._movez = StringVar()
        self._movez.set("0")

        self._move_roll = StringVar()
        self._move_roll.set("0")

        self._move_pitch = StringVar()
        self._move_pitch.set("0")

        self._move_yaw = StringVar()
        self._move_yaw.set("0")

        self._angles = []
        for i in range(6):
            self._angles.append(StringVar())
            self._angles[i].set("0")

    def __init_listener__(self):
        self._status_listener = StatusListener(self._controller)
        self._status_listener.set_update_callback(self._update_status)
        self._status_listener.start()

        self.btn_enable_listener.config(command=self.__enable_listener__)
        self.btn_disable_listener.config(command=self.__disable_listener__)

    def __createWidgets__(self):
        self.__calibration__(0)
        self.__hold_and_release__(2)
        self.__axis_move__(5)
        self.__arm_move__(9)
        self.__pose_zone__(15)

    def __update_hold_status__(self):
        self.__hold_status__ = self._controller.get_released_status()

    ###############################   calibration  ##################################
    def __calibration__(self, start_row):
        self.lb_calibration = Label(self, text='Calibration', width=10)
        self.lb_calibration.grid(row=start_row, column=3, columnspan=2, ipady=10)

        self.lb_calitype = Label(self, text='Mode', anchor='e', width=6)
        self.lb_calitype.grid(row=start_row+1, padx=6, column=0)

        self._calitype = StringVar()
        self.cb_calitype = Combobox(self, width=12, value=self._CALI_TYPE,
                                    textvariable=self._calitype, state="readonly")
        self.cb_calitype.current(0)
        self.cb_calitype.grid(row=start_row+1, column=1, columnspan=2, padx=8, pady=6)

        self.btn_calibrate = Button(self, text='Calibrate', width=8,
                                      command=self.__calibrate__)
        self.btn_calibrate.grid(row=start_row + 1, column=3, columnspan=2, sticky=W, pady=6)

        self.btn_reset = Button(self, text='Reset', width=6,
                                      command=self.__reset__)
        self.btn_reset.grid(row=start_row + 1, column=6, sticky=W, pady=6)

    def __calibrate__(self):
        try:
            self._controller.calibrate(self._CALI_VALUE[self._calitype.get()])
            self.cb_calitype.config(state="disabled")
            self.btn_calibrate.config(state=DISABLED)
        except Exception as e:
            print(str(e))

    def __reset__(self):
        try:
            self._controller.reset()
        except Exception as e:
            print(str(e))

    ############################### release & hold ##################################
    def __hold_and_release__(self, start_row):
        self.lb_calibration = Label(self, text='Hold & Release', width=12)
        self.lb_calibration.grid(row=start_row, column=3, columnspan=2, ipady=10)

        self.lb_release = Label(self, text='Release', anchor='e', width=6)
        self.lb_release.grid(row=start_row+1, padx=6, column=0)

        self.btn_release_all = Button(self, text='All', width=6,
                                      command=self.__release__)
        self.btn_release_all.grid(row=start_row+1, column=1, padx=8, pady=6)

        self.btn_release = []
        for i in range(6):
            self.btn_release.append(Button(self, text=str(i + 1), width=6,
                                           command=lambda x=i:self.__release__(x)))
            self.btn_release[i].grid(row=start_row+1, column=i + 2, padx=2, pady=6)

        self.lb_hold = Label(self, text='Hold', anchor='e', width=6)
        self.lb_hold.grid(row=start_row+2, padx=6, column=0)
        self.btn_hold_all = Button(self, text='All', width=6, state=DISABLED,
                                   command=self.__hold__)
        self.btn_hold_all.grid(row=start_row+2, column=1, padx=8, pady=6)

        self.btn_hold = []
        for i in range(6):
            self.btn_hold.append(Button(self, text=str(i + 1), width=6, state=DISABLED,
                                        command=lambda x=i:self.__hold__(x)))
            self.btn_hold[i].grid(row=start_row+2, column=i + 2, padx=2, pady=6)

    def __release__(self, index=None):
        if index is None:
            self._controller.release()
        else:
            self._controller.release({str(index+1)})
        self.__update_hold_status__()
        self.__switch_rh_btn_state__()

    def __hold__(self, index=None):
        if index is None:
            self._controller.hold()
        else:
            self._controller.hold({str(index+1)})

        self.__update_hold_status__()
        self.__switch_rh_btn_state__()

    def __switch_rh_btn_state__(self):
        count = 0
        for i in range(len(self.__hold_status__)):
            if self.__hold_status__[i]:
                self.btn_hold[i].config(state=NORMAL)
                self.btn_release[i].config(state=DISABLED)
            else:
                count += 1
                self.btn_hold[i].config(state=DISABLED)
                self.btn_release[i].config(state=NORMAL)

        if count == 0:
            self.btn_release_all.config(state=DISABLED)
            self.btn_hold_all.config(state=NORMAL)
            self.__axis_section_show__(False)
        elif count == 6:
            self.btn_release_all.config(state=NORMAL)
            self.btn_hold_all.config(state=DISABLED)
            self.__axis_section_show__(True)
        else:
            self.btn_release_all.config(state=NORMAL)
            self.btn_hold_all.config(state=NORMAL)
            self.__axis_section_show__(False)

    ###############################   axis move   ###################################
    def __axis_move__(self, start_row):
        self.lb_axis_move = Label(self, text='Axis Move')
        self.lb_axis_move.grid(row=start_row, column=3, columnspan=2, ipady=10)

        self.lb_velocity = Label(self, text='Velocity', anchor='e')
        self.lb_velocity.grid(row=start_row + 1, column=0)

        self.entry_velocity = Entry(self, width=8, textvariable=self._velocity,
                                    validate='all', validatecommand=self.__validateVelocity__)
        self.entry_velocity.grid(row=start_row + 1, column=1)

        self.lb_gripper = Label(self, text='Gripper', anchor='e')
        self.lb_gripper.grid(row=start_row+2, column=0, rowspan=2)
        self.btn_open_gripper = Button(self, text='open', width=8,
                                      command=self.__open_gripper__)
        self.btn_open_gripper.grid(row=start_row+2, column=1, padx=8, pady=6)

        self.btn_close_gripper = Button(self, text='close', width=8,
                                       command=self.__close_gripper__)
        self.btn_close_gripper.grid(row=start_row+3, column=1, padx=8, pady=6)

        self.btn_move_left = []
        self.btn_move_right = []
        self.lb_axis_name = []

        for i in range(3):
            for j in range(2):
                axis_index = i * 2 + j
                self.btn_move_left.append(Button(self, text='◄', width=4))
                self.btn_move_left[axis_index].bind('<Button-1>', lambda x,i=axis_index: self.__move_left__(x,i))
                self.btn_move_left[axis_index].bind('<ButtonRelease-1>', self.__pause__)
                self.btn_move_left[axis_index].grid(row=start_row+1+i, column=3*j+2, sticky=E)

                self.lb_axis_name.append(Label(self, text='Axis '+str(axis_index+1), width=6))
                self.lb_axis_name[axis_index].grid(row=start_row+1+i, column=3*j+3)

                self.btn_move_right.append(Button(self, text='►', width=4))
                self.btn_move_right[axis_index].bind('<Button-1>', lambda x,i=axis_index: self.__move_right__(x,i))
                self.btn_move_right[axis_index].bind('<ButtonRelease-1>', self.__pause__)
                self.btn_move_right[axis_index].grid(row=start_row+1+i, column=3*j+4, sticky=W)

    def __move_left__(self, event, axis_index):
        if not self._onMotion and self.btn_hold_all['state'] == DISABLED:
            self._onMotion = True
            _low = self._angles_limit[axis_index][0]
            self._controller.move_joint(axis_index+1, _low , velocity=int(self._velocity.get()), block=False)

    def __move_right__(self, event, axis_index):
        if not self._onMotion and self.btn_hold_all['state'] == DISABLED:
            self._onMotion = True
            _upper = self._angles_limit[axis_index][1]
            self._controller.move_joint(axis_index+1, _upper, velocity=int(self._velocity.get()), block=False)

    def __pause__(self, event):
        if self._onMotion:
            self._onMotion = False
            self._controller.pause()

    def __axis_section_show__(self, flag):
        if flag:
            self.__axis_move__(5)
        else:
            self.lb_axis_move.grid_forget()
            self.lb_velocity.grid_forget()
            self.entry_velocity.grid_forget()
            self.btn_open_gripper.grid_forget()
            self.btn_close_gripper.grid_forget()
            self.lb_gripper.grid_forget()
            for i in range(6):
                self.btn_move_left[i].grid_forget()
                self.btn_move_right[i].grid_forget()
                self.lb_axis_name[i].grid_forget()

    def __validateVelocity__(self):
        val = self._velocity.get()
        if val.isdigit():
            return True
        self._velocity.set("10")
        return False

    ################################  gripper  ####################################
    def __open_gripper__(self):
        self._controller.set_hand_signal('open')

    def __close_gripper__(self):
        self._controller.set_hand_signal('close')

    ###############################  Arm Move  #####################################
    def __arm_move__(self, start_row):
        self.lb_arm_move = Label(self, text='Position')
        self.lb_arm_move.grid(row=start_row, column=3, columnspan=2, ipady=10)

        self.lb_xyz_pos = Label(self, text='Coords', anchor='e')
        self.lb_xyz_pos.grid(row=start_row + 1, column=0, rowspan=2)

        self.btn_move_pos = Button(self, text='Move to', width=8, height=2, command=self.__move_coords__)
        self.btn_move_pos.grid(row=start_row+1, column=1, rowspan=2)

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

        self.entry_x = Entry(self, width=6, textvariable=self._move_x)
        self.entry_x.grid(row=start_row + 2, column=2)

        self.entry_y = Entry(self, width=6, textvariable=self._move_y)
        self.entry_y.grid(row=start_row + 2, column=3)

        self.entry_z = Entry(self, width=6, textvariable=self._movez)
        self.entry_z.grid(row=start_row + 2, column=4)

        self.entry_roll = Entry(self, width=6, textvariable=self._move_roll)
        self.entry_roll.grid(row=start_row + 2, column=5)

        self.entry_pitch = Entry(self, width=6, textvariable=self._move_pitch)
        self.entry_pitch.grid(row=start_row + 2, column=6)

        self.entry_yaw = Entry(self, width=6, textvariable=self._move_yaw)
        self.entry_yaw.grid(row=start_row + 2, column=7)

        self.lb_blank = Label(self, text='')
        self.lb_blank.grid(row=start_row + 3)

        self.lb_angles_pos = Label(self, text='Angels', anchor='e')
        self.lb_angles_pos.grid(row=start_row + 4, column=0, rowspan=2)

        self.btn_move_angles = Button(self, text='Move to', width=8, height=2, command=self.__move_angles__)
        self.btn_move_angles.grid(row=start_row + 4, column=1, rowspan=2)

        self.lb_angle = []
        for i in range(6):
            self.lb_angle.append(Label(self, text="Axis "+str(i+1), width=6))
            self.lb_angle[i].grid(row=start_row + 4, column=i + 2, padx=2)

        self.entry_angle = []
        for i in range(6):
            self.entry_angle.append(Entry(self, textvariable=self._angles[i], width=6))
            self.entry_angle[i].grid(row=start_row + 5, column=i + 2, padx=2)

    def __move_coords__(self):
        tx = float(self.entry_x.get())
        ty = float(self.entry_y.get())
        tz = float(self.entry_z.get())
        try:
            self._controller.move_point(tx, ty, tz)
        except Exception:
            pass

    def __move_angles__(self):
        angles = [float(self.entry_angle[0].get()), float(self.entry_angle[1].get()), float(self.entry_angle[2].get()),
                  float(self.entry_angle[3].get()), float(self.entry_angle[4].get()), float(self.entry_angle[5].get())]
        try:
            self._controller.move_angles(angles)
        except Exception:
            pass

    def __enable_listener__(self):
        self._status_listener.enable()
        self.btn_enable_listener.config(state=DISABLED)
        self.btn_disable_listener.config(state=NORMAL)

    def __disable_listener__(self):
        self._status_listener.disable()
        self.btn_enable_listener.config(state=NORMAL)
        self.btn_disable_listener.config(state=DISABLED)

    ################################  Pose  ######################################
    def __pose_zone__(self, start_row):
        Label(self, text="Save as").grid(row=start_row, column=0, pady=12)

        self.entry_posename = Entry(self, width=17)
        self.entry_posename.grid(row=start_row, column=1, columnspan=2)

        self.btn_savepose = Button(self, text="Save", command=self.__save_pose__)
        self.btn_savepose.grid(row=start_row, column=3)

        self.btn_enable_listener = Button(self, text="Enable", state=DISABLED)
        self.btn_enable_listener.grid(row=start_row, column=6)

        self.btn_disable_listener = Button(self, text="Disable", state=NORMAL)
        self.btn_disable_listener.grid(row=start_row, column=7)

    def __save_pose__(self):
        name = self.entry_posename.get()
        if not(name is None or name == ""):
            self._controller.save_pose(name)

    ################################  Status  #####################################
    def _update_status(self, position, posture):
        for i in range(len(position)):
            self._angles[i].set(str(position[i]))
        self._move_x.set(str(posture[0]))
        self._move_y.set(str(posture[1]))
        self._movez.set(str(posture[2]))
        self._move_roll.set(str(posture[3][0]))
        self._move_pitch.set(str(posture[3][1]))
        self._move_yaw.set(str(posture[3][2]))

    def destroy(self):
        try:
            self._status_listener.stop()
            self._controller.finalize()
        except Exception:
            pass