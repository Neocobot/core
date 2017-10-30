import inspect
import os
import threading

import cv2
import numpy as np
import time

from project.pickball.managers import WindowManager, CaptureManager


class monitor(threading.Thread):

    range = 40
    mutex = threading.Lock()
    file_path = os.path.abspath(os.path.dirname(inspect.stack()[0][1]))
    on_move = False

    def set_after_catch(self, after_catch):
        self._after_catch = after_catch
    
    def __init__(self, callback=None, after_catch=None, camera=1):
        threading.Thread.__init__(self)
        # frame operation delay
        self.frame = None
        self._callback = callback
        self._after_catch = after_catch

        [self.W, self.H] =np.loadtxt(os.path.join(self.file_path, 'size'), np.int).tolist()
        #self.OFFSET = int((640 - self.W) / 2)

        self.CENTER_X = int(self.W / 2)
        self.CENTER_Y = int(self.H / 2)

        # window name
        self._Window_name = 'monitor'
        self._trackbar_name = 'trackbar'
        self._trackbar_LHchannel = "LHchannel"
        self._trackbar_LSchannel = "LSchannel"
        self._trackbar_LVchannel = "LVchannel"
        self._trackbar_HHchannel = "HHchannel"
        self._trackbar_HSchannel = "HSchannel"
        self._trackbar_HVchannel = "HVchannel"
        self._txt_name = 'channel-background.txt'

        # coordinate 
        self._record_coordinate = []
        self._centeral_coordinate = []
        self._remain_coordinate = []
        self._object_count = 0
        self._show_count = 0

        # image 
        self._srcRGB = 0

        self._Channel = np.loadtxt(os.path.join(self.file_path,self._txt_name), np.int)
        self._LHchannel = 0
        self._LSchannel = 0
        self._LVchannel = 0
        self._HHchannel = 0
        self._HSchannel = 0
        self._HVchannel = 0

        # flag
        self._background_flag = True
        self._save_flag = None

        # window and camera init
        self._windowManager = WindowManager(self._Window_name)
        self._captureManager = CaptureManager(cv2.VideoCapture(camera), self._windowManager, False)

        self._windowManager.createWindow()
        self._windowManager.start()
        self.is_start = False

    def filter(self, src, low, high, ksize_open, ksize_close, flag):
        """filter."""
        lowHSV = np.array(low)
        highHSV = np.array(high)
        src_Filter = cv2.medianBlur(src, 5)
        src_Filter = cv2.inRange(src_Filter, lowHSV, highHSV)
        #src_Filter = cv2.GaussianBlur(src, (5,5), 0)
        if flag == True:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(ksize_open, ksize_open))
            src_Filter = cv2.morphologyEx(src_Filter, cv2.MORPH_OPEN, kernel)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(ksize_close, ksize_close))
            src_Filter = cv2.morphologyEx(src_Filter, cv2.MORPH_CLOSE, kernel)
        return src_Filter

    def find_contours(self, src, MINAREA, abandon, color):
        """input image and MINAREA."""
        src, contours, hier = cv2.findContours(src, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            Length = cv2.arcLength(cnt, 0)
            if Length < MINAREA:
                continue
            if Length >= MINAREA:
                self._object_count += 1
                # draw circle
                (x,y),radius = cv2.minEnclosingCircle(cnt)
                (x,y) = (int(x),int(y))
                radius = int(radius)
                # calculate center
                M = cv2.moments(cnt)
                cX = int(M['m10'] / M['m00'])
                cY = int(M['m01'] / M['m00'])
                width = src.shape[1]
                heigth = src.shape[0]
                if cX > abandon and cX < width - abandon and cY > abandon and cY < heigth - abandon:
                    self._centeral_coordinate.append((cX, cY, color, radius, x, y))

    def backgroundcatch(self, frame):
        self._srcRGB = frame

        # convert to hsv and equalize it
        hsv = cv2.cvtColor(self._srcRGB, cv2.COLOR_BGR2HSV)
        (img_h, img_s, img_v) = cv2.split(hsv)
        img_v = cv2.equalizeHist(img_v)
        hsv = cv2.merge((img_h, img_s, img_v))

        # Green image filter
        lowHSV = self._Channel[0]
        highHSV = self._Channel[1]

        background = self.filter(hsv, lowHSV, highHSV, 9, 13, True)
        value = cv2.mean(background)[0]

        #if value <= 150.0:
        #    print('background: black')
        #    self._txt_name = 'channel-black.txt'
        #else :
        print('background: white')
        self._txt_name = 'channel-white.txt'

        self._Channel = np.loadtxt(os.path.join(self.file_path,self._txt_name), np.int)
        self._background_flag = False

    def camcatch(self):
        if self.frame is not None:
            # convert to hsv and equalize it
            hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
            (img_h, img_s, img_v) = cv2.split(hsv)
            img_v = cv2.equalizeHist(img_v)
            hsv = cv2.merge((img_h, img_s, img_v))

            # Green image filter
            lowHSV = self._Channel[0]
            highHSV = self._Channel[1]
            green = self.filter(hsv, lowHSV, highHSV, 9, 13, True)

            # Blue image filter
            lowHSV = self._Channel[2]
            highHSV = self._Channel[3]
            blue = self.filter(hsv, lowHSV, highHSV, 9, 13, True)

            # Red image filter
            lowHSV = self._Channel[4]
            highHSV = self._Channel[5]
            red_1 = self.filter(hsv, lowHSV, highHSV, 3, 9, True)

            lowHSV = [155, self._Channel[4, 1], self._Channel[4, 2]]
            highHSV = [180, self._Channel[5, 1], self._Channel[5, 2]]
            red_2 = self.filter(hsv, lowHSV, highHSV, 3, 9, True)
            red = red_1 + red_2

            # find contours and ger central coordinate
            self._object_count = 0
            self._centeral_coordinate = []
            self.find_contours(green, 40.0, 10, 'green')
            self.find_contours(blue, 60.0, 10, 'blue')
            self.find_contours(red, 40.0, 10, 'red')

            Same_coordinate = []
            NotSame_coordinate = []
            Index = []
            if self._centeral_coordinate == [] or self._record_coordinate == []:
                self._record_coordinate = self._centeral_coordinate
            else:
                for j in range(len(self._record_coordinate)):
                    for i in range(len(self._centeral_coordinate)):
                        sum = abs(self._centeral_coordinate[i][1] - self._record_coordinate[j][1]) + abs(
                            self._centeral_coordinate[i][0] - self._record_coordinate[j][0])
                        if sum <= 4:
                            Same_coordinate.append(self._record_coordinate[j])
                            Index.append(i)
                for j in range(len(self._centeral_coordinate)):
                    flag = False
                    for i in range(len(Index)):
                        if j == Index[i]:
                            flag = True
                    if flag == False:
                        NotSame_coordinate.append(self._centeral_coordinate[j])
                self._record_coordinate = []
                Same_coordinate[len(Same_coordinate):len(Same_coordinate)] = NotSame_coordinate
                self._record_coordinate = Same_coordinate

            if NotSame_coordinate == [] and self._record_coordinate != []:
                self._show_count += 1
                if self._show_count == 10:
                    self._remain_coordinate = self._record_coordinate
                    self._show_count = 0

            elif NotSame_coordinate == [] and self._record_coordinate == []:
                self._show_count = 0
                self._remain_coordinate = []

            else:
                self._show_count = 0

            # draw
            for cnt in range(len(self._record_coordinate)):
                (cX, cY, color, radius, x, y) = self._record_coordinate[cnt]
                # centeral coordinate
                cv2.circle(self.frame, (cX, cY), 3, (0, 0, 255), -1)
                # draw drawContours
                cv2.circle(self.frame, (cX, cY), radius, (0, 255, 0), 2)
                # put number text
                try:
                    cv2.putText(self.frame, str(cnt + 1), (cX - 10, cY - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                except IndexError as e:
                    print(str(e))

            cv2.rectangle(self.frame,
                          (self.CENTER_X - self.range, self.CENTER_Y - self.range),
                          (self.CENTER_X + self.range, self.CENTER_Y + self.range),
                          color=(255, 0, 0))

            # press b g r to show image and trackbar / press c to close
            if self._save_flag == 'Green':
                cv2.imshow(self._trackbar_name, green[0:self.H, 0:self.W])
                cv2.waitKey(1)
            elif self._save_flag == 'Blue':
                pass
                cv2.imshow(self._trackbar_name, blue[0:self.H, 0:self.W])
                cv2.waitKey(1)
            elif self._save_flag == 'Red':
                pass
                cv2.imshow(self._trackbar_name, red[0:self.H, 0:self.W])
                cv2.waitKey(1)
            else:
                cv2.destroyWindow(self._trackbar_name)


    def on_TrackChange(self, x):
        if self._txt_name == 'channel-white.txt':
            self._LSchannel = cv2.getTrackbarPos(self._trackbar_LSchannel, self._trackbar_name)
        if self._txt_name == 'channel-black.txt':
            self._LVchannel = cv2.getTrackbarPos(self._trackbar_LVchannel, self._trackbar_name)

        if self._save_flag == 'Green':
            self._Channel[0] = np.array([self._LHchannel, self._LSchannel, self._LVchannel])
            self._Channel[1] = np.array([self._HHchannel, self._HSchannel, self._HVchannel])
        elif self._save_flag == 'Blue':
            self._Channel[2] = np.array([self._LHchannel, self._LSchannel, self._LVchannel])
            self._Channel[3] = np.array([self._HHchannel, self._HSchannel, self._HVchannel])
        elif self._save_flag == 'Red':
            self._Channel[4] = np.array([self._LHchannel, self._LSchannel, self._LVchannel])
            self._Channel[5] = np.array([self._HHchannel, self._HSchannel, self._HVchannel])

        np.savetxt(os.path.join(self.file_path, self._txt_name), self._Channel, "%d", ' ', '\r\n')

    def config_adjust(self, keycode):
        if keycode == 103 or keycode == 98 or keycode == 114 : # g b r

            cv2.namedWindow(self._trackbar_name)
            if keycode == 103: # g
                if self._save_flag == 'Green':
                    self._save_flag = None
                    return
                print('(Trackbar) : create trackbar for Green image')
                print('channel value : \n', self._Channel[0:2])
                self._LHchannel = self._Channel[0,0]
                self._LSchannel = self._Channel[0,1]
                self._LVchannel = self._Channel[0,2]
                self._HHchannel = self._Channel[1,0]
                self._HSchannel = self._Channel[1,1]
                self._HVchannel = self._Channel[1,2]
                self._save_flag = 'Green'

            if keycode == 98: # b
                if self._save_flag == 'Blue':
                    self._save_flag = None
                    return
                print('(Trackbar) : create trackbar for Blue image')
                print('channel value : \n', self._Channel[2:4])
                self._LHchannel = self._Channel[2,0]
                self._LSchannel = self._Channel[2,1]
                self._LVchannel = self._Channel[2,2]
                self._HHchannel = self._Channel[3,0]
                self._HSchannel = self._Channel[3,1]
                self._HVchannel = self._Channel[3,2]
                self._save_flag = 'Blue'

            if keycode == 114: # r
                if self._save_flag == 'Red':
                    self._save_flag = None
                    return
                print('(Trackbar) : create trackbar for Red image')
                print('channel value : \n', self._Channel[4:6])
                self._LHchannel = self._Channel[4,0]
                self._LSchannel = self._Channel[4,1]
                self._LVchannel = self._Channel[4,2]
                self._HHchannel = self._Channel[5,0]
                self._HSchannel = self._Channel[5,1]
                self._HVchannel = self._Channel[5,2]
                self._save_flag = 'Red'

            if self._txt_name == 'channel-white.txt':
                cv2.createTrackbar(self._trackbar_LSchannel, self._trackbar_name, self._LSchannel, 255, self.on_TrackChange)
            if self._txt_name == 'channel-black.txt':
                cv2.createTrackbar(self._trackbar_LVchannel, self._trackbar_name, self._LVchannel, 255, self.on_TrackChange)

        elif keycode == 87: # W
            self._txt_name = 'channel-white.txt'
            self._Channel = np.loadtxt(self._txt_name, np.int)
            self._background_flag = False
            
        elif keycode == 66: # B
            self._txt_name = 'channel-black.txt'
            self._Channel = np.loadtxt(self._txt_name, np.int)
            self._background_flag = False

    def _callback_func(self):
        while self._windowManager.isWindowCreated:
            while self.on_move:
                time.sleep(0.05)
            if len(self._remain_coordinate) > 0:
                (cX, cY, color, radius, x, y) = self._remain_coordinate[0]
                self.on_move = True
                self._callback(cX, cY, color=color)

            time.sleep(0.02)

    def after_catch(self):
        if len(self._remain_coordinate) == 0 and self._after_catch is not None:
            self._after_catch()
        self.on_move = False


    def run(self):
        """Run the main loop."""
        if self._callback is not None:
            threading.Thread(target=self._callback_func, args=()).start()
        while self._windowManager.isWindowCreated:
            try:
                self._captureManager.enterFrame()
                self.frame = self._captureManager.frame
                if self.is_start:
                    if self.frame is not None and self._background_flag == False:
                        self.camcatch()
                    if self.frame is not None and self._background_flag == True:
                        self.backgroundcatch(self.frame)
                    #time.sleep(0.01)
            except Exception as e:
                print(str(e))
            finally:
                #print(time.time())
                self._captureManager.exitFrame()
            #self._windowManager.processEvents()
            time.sleep(0.01)

    def close(self):
        self.set_stop()
        self._windowManager.destroyAllWindow()
        cv2.destroyAllWindows()

    def set_start(self):
        self.is_start = True

    def set_stop(self):
        self.is_start = False
        self._remain_coordinate = []


