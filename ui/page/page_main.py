'''
@Project: Neocobot

@Created: 23-Oct-2017 by Chen Zhuo

'''
from tkinter import *

from ui.frame.frame_control import FRAME_CONTROL
from ui.frame.frame_project import FRAME_PROJECT
from ui.frame.frame_pickball import FRAME_PICKBALL


class PAGE_MAIN(object):
    def __init__(self, controller, master=None):
        self.root = master
        self.root.geometry('%dx%d' % (480, 600))
        self._controller = controller
        self.createPage()

    def createPage(self):
        self.controlFrame = FRAME_CONTROL(self._controller, self.root)
        self.pickballFrame = FRAME_PICKBALL(self._controller, self.root)
        self.projectFrame = FRAME_PROJECT(self._controller, self.root)
        self.controlFrame.pack()

        menubar = Menu(self.root)
        menubar.add_command(label='Projects', command=self.__project_frame__)
        menubar.add_command(label='ControlBoard', command=self.__control_frame__)
        menubar.add_command(label='Demo', command=self.__pickball_frame__)
        self.root['menu'] = menubar

    def __control_frame__(self):
        self.controlFrame.pack()
        self.pickballFrame.pack_forget()
        self.projectFrame.pack_forget()
        self.root.geometry('%dx%d' % (480, 600))

    def __pickball_frame__(self):
        self.pickballFrame.pack()
        self.controlFrame.pack_forget()
        self.projectFrame.pack_forget()
        self.root.geometry('%dx%d' % (320, 300))

    def __project_frame__(self):
        self.projectFrame.pack()
        self.pickballFrame.pack_forget()
        self.controlFrame.pack_forget()
        self.root.geometry('%dx%d' % (480, 300))