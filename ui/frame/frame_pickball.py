'''
@Project: Neocobot

@Created: 23-Oct-2017 by Chen Zhuo

'''
from tkinter import *
from tkinter.ttk import Combobox

from project.pickball.calibrate import Calibrate
from project.pickball.catch import monitor

VELOCITY = 40

VERTICAL_DOWN = [0,-90, 180]
FOWARD_ORIENTATION = [0,-90, 180]#[180, -80, 0]
BACKWARD_ORINTATION = [0,-90, 180]#[0, -80, 180]

LAY_BALL_COORDS = [400, 150]

HEIGHT = 120

move_point = lambda x, y, z, r=False, o=VERTICAL_DOWN, v=VELOCITY: 'move_point(%(x)d, %(y)d, %(z)d, orientation=%(o)s, velocity=%(v)d, relative=%(r)s)\r\n' % {'x':x, 'y':y, 'z':z, 'r':r, 'o':o, 'v':v}
open_gripper = 'set_hand_signal(\'open\')\r\n'
close_gripper = 'set_hand_signal(\'close\')\r\n'
reset = 'reset()\r\n'


class FRAME_PICKBALL(Frame):

    def __init__(self, controller, master=None):
        Frame.__init__(self, master)
        self.root = master
        self._controller = controller
        self.__init_params__()
        self.__createWidgets__()

    def __init_params__(self):
        self._c = Calibrate()
        self._m = None
        self._movex = StringVar()
        self._movex.set("200")

        self._movey = StringVar()
        self._movey.set("200")

        self._movez = StringVar()
        self._movez.set("200")

    def __createWidgets__(self, start_row = 0):

        self.btn_show = Button(self, text='Show Monitor', command=self.__show_monitor__, width=15, height=2)
        self.btn_show.grid(row=start_row + 1, column=0, columnspan=3, padx=6, pady=2)

        self.btn_close = Button(self, text='Close Monitor', command=self.__close_monitor__, width=15, height=2)
        self.btn_close.grid(row=start_row + 1, column=3, columnspan=3, padx=6, pady=2)
        self.btn_close.config(state=DISABLED)

        self.btn_start = Button(self, text='Start Catch', command=self.start, width=15, height=2)
        self.btn_start.grid(row=start_row + 2, column=0, columnspan=3, padx=6, pady=2)
        self.btn_start.config(state=DISABLED)

        self.btn_stop = Button(self, text='Stop Catch', command=self.stop, width=15, height=2)
        self.btn_stop.grid(row=start_row + 2, column=3, columnspan=3, padx=6, pady=2)
        self.btn_stop.config(state=DISABLED)

        self.btn_upper_left = Button(self, text='Upper Left', command=lambda: self.set(3), width=15, height=2)
        self.btn_upper_left.grid(row=start_row + 4, column=0, columnspan=3, padx=6, pady=2)
        self.btn_upper_left.config(state=NORMAL)

        self.btn_upper_right = Button(self, text='Upper Right', command=lambda: self.set(2), width=15, height=2)
        self.btn_upper_right.grid(row=start_row + 4, column=3, columnspan=3, padx=6, pady=2)
        self.btn_upper_right.config(state=NORMAL)

        self.btn_lower_left = Button(self, text='Lower Left', command=lambda: self.set(1), width=15, height=2)
        self.btn_lower_left.grid(row=start_row + 5, column=0, columnspan=3, padx=6, pady=2)
        self.btn_lower_left.config(state=NORMAL)

        self.btn_lower_right = Button(self, text='Lower Right', command=lambda: self.set(0), width=15, height=2)
        self.btn_lower_right.grid(row=start_row + 5, column=3, columnspan=3, padx=6, pady=2)
        self.btn_lower_right.config(state=NORMAL)

        self.btn_pos_confirm = Button(self, text='Move To:', command=self.__move_coor__, width=15, height=3)
        self.btn_pos_confirm.grid(row=start_row + 6, rowspan=3, column=0, columnspan=3)

        Label(self, text='X:').grid(row=start_row + 6, column=3, sticky=W)
        Label(self, text='Y:').grid(row=start_row + 7, column=3, sticky=W)
        Label(self, text='Z:').grid(row=start_row + 8, column=3, sticky=W)

        self.entry_x = Entry(self, width=9, textvariable=self._movex)
        self.entry_x.grid(row=start_row + 6, column=4, columnspan=2)

        self.entry_y = Entry(self, width=9, textvariable=self._movey)
        self.entry_y.grid(row=start_row + 7, column=4, columnspan=2)

        self.entry_z = Entry(self, width=9, textvariable=self._movez)
        self.entry_z.grid(row=start_row + 8, column=4, columnspan=2)

    def reset(self):
        self._controller.run_script_code(close_gripper)
        self._controller.reset()

    def __show_monitor__(self):
        self.btn_show.config(state=DISABLED)
        self.btn_close.config(state=NORMAL)
        self.btn_start.config(state=NORMAL)
        if self._controller is not None:
            self._m = monitor(self.catch, self.reset, camera=1)
        else:
            self._m = monitor(camera=0)
        self._m.start()

    def __close_monitor__(self):
        self.stop()
        self.btn_start.config(state=NORMAL)
        self.btn_show.config(state=NORMAL)
        self.btn_close.config(state=DISABLED)
        self.btn_start.config(state=DISABLED)
        self.btn_stop.config(state=DISABLED)
        if self._m is not None:
            self._m.close()
            self._m = None

    def start(self):
        self.btn_start.config(state=DISABLED)
        self.btn_stop.config(state=NORMAL)
        self._m.set_start()

    def stop(self):
        self.btn_start.config(state=NORMAL)
        self.btn_stop.config(state=DISABLED)
        self._m.set_stop()

    def set(self, index):
        posture = self._controller.get_posture()
        self._c.set_point(index, posture[0], posture[1])

    def reset(self):
        self._controller.reset()

    def catch(self, x, y, z=HEIGHT, color=None):

        def make_script(scripts):
            script = ''
            for s in scripts:
                script += s
            return script

        _x, _y = self._c.get(x, y)
        put_x, put_y = LAY_BALL_COORDS[0], LAY_BALL_COORDS[1]

        scripts = []

        def correct(x, y, _x, _y):
            if y < 30 and 300 < x:
                _x, _y = self._c.get(x, 40)
                return _x, _y, BACKWARD_ORINTATION

            if y < 40 and 200 < x:
                _x, _y = self._c.get(x, 40)
                return _x, _y, VERTICAL_DOWN

            if y < 50 and 200 < x:
                _x, _y = self._c.get(x, 50)
                return _x, _y, VERTICAL_DOWN

            return (_x, _y, VERTICAL_DOWN) if y < 100 and x < 200 else (_x, _y, FOWARD_ORIENTATION)

        _x, _y, orient = correct(x, y, _x, _y)

        print(x, y, _x, _y)

        scripts.extend([  move_point(_x, _y, z + 70),
                            move_point(0, 0, -70, r=True, o=orient, v=60),
                            close_gripper,
                            move_point(0, 0, 70, r=True, v=60),
                            move_point(put_x, put_y, z, o=VERTICAL_DOWN, v=40),
                            open_gripper])

        if len(scripts) > 0:
            print(scripts)
            self._controller.set_hand_signal('open')
            self._controller.run_script_code(make_script(scripts), callback=self._m.after_catch if self._m is not None else None)

    def __move_coor__(self):
        tx = self.entry_x.get()
        ty = self.entry_y.get()
        tz = self.entry_z.get()
        try:
            x = int(tx)
            y = int(ty)
            _x, _y = self._c.get(x, y)
            self._controller.run_script_code(move_point(_x, _y, int(tz)))
        except Exception as e:
            print(str(e))