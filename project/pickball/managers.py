import inspect
import os
import threading

import cv2
import numpy
import numpy as np
import time

class CaptureManager(object):
    file_path = os.path.abspath(os.path.dirname(inspect.stack()[0][1]))
    
    def __init__(self, capture, previewWindowManager = None,
                 shouldMirrorPreview = False):

        [self.W, self.H] =np.loadtxt(os.path.join(self.file_path, 'size'), np.int).tolist()
        self.OFFSET = int((640 - self.W) / 2)
        
        self.previewWindowManager = previewWindowManager
        self.shouldMirrorPreview = shouldMirrorPreview
        
        self._capture = capture
        self._channel = 0
        self._enteredFrame = False
        self._frame = None
        self._imageFilename = None
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None
        
        self._startTime = None
        self._framesElapsed = int(0)
        self._fpsEstimate = None
    
    @property
    def channel(self):
        return self._channel
    
    @channel.setter
    def channel(self, value):
        if self._channel != value:
            self._channel = value
            self._frame = None
    
    @property
    def frame(self):
        if self._enteredFrame and self._frame is None:
            _, frame = self._capture.retrieve()
            self._frame = frame.copy()[0:self.H, self.OFFSET:self.W + self.OFFSET]
        return self._frame
    
    @property
    def isWritingImage(self):
        return self._imageFilename is not None
    
    @property
    def isWritingVideo(self):
        return self._videoFilename is not None
    
    def enterFrame(self):
        """Capture the next frame, if any."""
        
        # But first, check that any previous frame was exited.
        assert not self._enteredFrame, \
            'previous enterFrame() had no matching exitFrame()'
        
        if self._capture is not None:
            self._enteredFrame = self._capture.grab()
    
    def exitFrame(self):
        """Draw to the window. Write to files. Release the frame."""
        
        # Check whether any grabbed frame is retrievable.
        # The getter may retrieve and cache the frame.
        if self.frame is None:
            self._enteredFrame = False
            return
        
        # Update the FPS estimate and related variables.
        if self._framesElapsed == 0:
            self._startTime = time.time()
        else:
            timeElapsed = time.time() - self._startTime
            self._fpsEstimate =  self._framesElapsed / timeElapsed
        self._framesElapsed += 1
        
        # Draw to the window, if any.
        if self.previewWindowManager is not None:
            if self.shouldMirrorPreview:
                mirroredFrame = numpy.fliplr(self._frame).copy()
                self.previewWindowManager.show(mirroredFrame)
            else:
                self.previewWindowManager.show(self._frame)
        
        # Write to the image file, if any.
        if self.isWritingImage:
            cv2.imwrite(self._imageFilename, self._frame)
            self._imageFilename = None
        
        # Write to the video file, if any.
        self._writeVideoFrame()
        
        # Release the frame.
        self._frame = None
        self._enteredFrame = False
    
    def writeImage(self, filename):
        """Write the next exited frame to an image file."""
        self._imageFilename = filename
    
    def startWritingVideo(
            self, filename,
            encoding = cv2.VideoWriter_fourcc('M','J','P','G')):
        """Start writing exited frames to a video file."""
        self._videoFilename = filename
        self._videoEncoding = encoding
    
    def stopWritingVideo(self):
        """Stop writing exited frames to a video file."""
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None
    
    def _writeVideoFrame(self):
        
        if not self.isWritingVideo:
            return
        
        if self._videoWriter is None:
            fps = self._capture.get(cv2.CAP_PROP_FPS)
            if fps <= 0.0:
                # The capture's FPS is unknown so use an estimate.
                if self._framesElapsed < 20:
                    # Wait until more frames elapse so that the
                    # estimate is more stable.
                    return
                else:
                    fps = self._fpsEstimate
            size = (int(self._capture.get(
                        cv2.CAP_PROP_FRAME_WIDTH)),
                    int(self._capture.get(
                        cv2.CAP_PROP_FRAME_HEIGHT)))
            self._videoWriter = cv2.VideoWriter(
                self._videoFilename, self._videoEncoding,
                fps, size)
        
        self._videoWriter.write(self._frame)

class WindowManager(threading.Thread):
    
    def __init__(self, windowName, keypressCallback = None):
        threading.Thread.__init__(self)
        self.frame = None
        self.keypressCallback = keypressCallback
        
        self._windowName = windowName
        self._isWindowCreated = False

    def run(self):
        while self._isWindowCreated:
            if self.frame is not None:
                cv2.imshow(self._windowName, self.frame)
                cv2.waitKey(1)
    
    @property
    def isWindowCreated(self):
        return self._isWindowCreated
    
    def createWindow(self):
        cv2.namedWindow(self._windowName)
        self._isWindowCreated = True
    
    def show(self, frame):
        self.frame = frame
        #cv2.imshow(self._windowName, frame)
        #cv2.waitKey(1)
    
    def destroyMainWindow(self):
        cv2.destroyWindow(self._windowName)
        self._isWindowCreated = False

    def destroyAllWindow(self):
        cv2.destroyAllWindows()
        self._isWindowCreated = False

    def processEvents(self):
        while self._isWindowCreated:
            try:
                keycode = cv2.waitKey(0)
                if self.keypressCallback is not None and keycode != 255:
                    # Discard any non-ASCII info encoded by GTK.
                    print(keycode)
                    keycode &= 0xFF
                    self.keypressCallback(keycode)
            except Exception as e:
                print(str(e))


