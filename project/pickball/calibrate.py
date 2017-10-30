import inspect
import os

import numpy as np

class Calibrate:
    file_path = os.path.abspath(os.path.dirname(inspect.stack()[0][1]))

    def __init__(self):
        self.cali_mark = np.loadtxt(os.path.join(self.file_path,'datum_mark.txt'), np.int).tolist()
        [self.W, self.H] =np.loadtxt(os.path.join(self.file_path, 'size'), np.int).tolist()

    def set_point(self, index, x, y):
        self.cali_mark[index] = [x, y]
        self.save()

    def save(self):
        np.savetxt(os.path.join(self.file_path,'datum_mark.txt'), self.cali_mark, "%d", ' ', '\r\n')

    def trans(self):
        x0 = self.cali_mark[0][0]
        x1 = self.cali_mark[1][0]
        x2 = self.cali_mark[2][0]
        x3 = self.cali_mark[3][0]
        y0 = self.cali_mark[0][1]
        y1 = self.cali_mark[1][1]
        y2 = self.cali_mark[2][1]
        y3 = self.cali_mark[3][1]

        matrix = [[self.W,      0,      0,      0, -self.W * x1,            0],
                  [     0, self.H,      0,      0,            0, -self.H * x2],
                  [self.W, self.H,      0,      0, -self.W * x3, -self.H * x3],
                  [     0,      0, self.W,      0, -self.W * y1,            0],
                  [     0,      0,      0, self.H,            0, -self.H * y2],
                  [     0,      0, self.W, self.H, -self.W * y3, -self.H * y3]]
        m = np.array(matrix)

        solution = [x1 - x0, x2 - x0, x3 - x0, y1 - y0, y2 - y0, y3 - y0]
        s = np.array(solution)

        params = np.linalg.solve(m, s)
        return params

    def get(self, u, v):
        u = self.W - u
        v = self.H - v
        params = self.trans()
        x = (params[0] * u + params[1] * v + self.cali_mark[0][0]) / (params[4] * u + params[5] * v +1)
        y = (params[2] * u + params[3] * v + self.cali_mark[0][1]) / (params[4] * u + params[5] * v +1)
        return int(x), int(y)

