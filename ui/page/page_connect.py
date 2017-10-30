'''
@Project: Neocobot

@Created: 23-Oct-2017 by Chen Zhuo

'''
from tkinter import *

from neocobot.NeoCobot import NeoCobot
from ui.page.page_main import PAGE_MAIN


class PAGE_CONN(object):
    __PARAMETERS__ = {'channel_name': '1', 'channel_type': 'PEAK_SYS_PCAN_USB',
                  'protocol': 'TMLCAN', 'host_id': 10, 'baud_rate': 500000}

    def __init__(self, master=None):
        self.root = master
        self.__HAND__ = IntVar()
        self.__HAND__.set(1)
        self.__createWidgets__()

    def __createWidgets__(self):
        self.page = Frame(self.root)
        self.page.pack()

        self.btn_connect = Button(self.page, text='Connect to Neocobot', command=self.__connect__,
                                  width=25, height=3)
        self.btn_connect.grid(row=0, column=0, columnspan=2)

        self.checkbtn_hand = Checkbutton(self.page, text='Add Gripper', variable=self.__HAND__)
        self.checkbtn_hand.grid(row=1, column=0, columnspan=2)


    def __connect__(self):
        controller = NeoCobot()

        hand = 'gripper' if self.__HAND__.get() == 1 else None
        try:
            controller.initialize(self.__PARAMETERS__, hand)
            self.page.destroy()
            PAGE_MAIN(controller, self.root)
        except Exception as e:
            del controller
            print(str(e))
