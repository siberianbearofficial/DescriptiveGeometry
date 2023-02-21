from utils.drawing.screen_point import ScreenPoint


class ScreenSegment:
    def __init__(self, plot, p1, p2, color=(0, 0, 0), thickness=3, line_type=1):
        if isinstance(p1, tuple):
            p1 = ScreenPoint(plot, *p1, color)
        if isinstance(p2, tuple):
            p2 = ScreenPoint(plot, *p2, color)
        self.p1 = p1
        self.p2 = p2
        self.plot = plot
        self.color = color
        self.thickness = thickness
        self.line_type = line_type
        if self.p2.x != self.p1.x:
            self.k = ((self.p2.y - self.p1.y) / (self.p2.x - self.p1.x))
            self.b = p1.y - self.k * p1.x
            self.x1 = min(p1.x, p2.x)
            self.x2 = max(p1.x, p2.x)
            if self.k > 0:
                min_x = max(self.x1, self.plot.tlp[0] + 2, self.x(self.plot.tlp[1] + 2))
                max_x = min(self.x2, self.plot.brp[0] - 2, self.x(self.plot.brp[1] - 2))
            elif self.k < 0:
                min_x = max(self.x1, self.plot.tlp[0] + 2, self.x(self.plot.brp[1] - 2))
                max_x = min(self.x2, self.plot.brp[0] - 2, self.x(self.plot.tlp[1] + 2))
            elif self.plot.tlp[1] < p1.y < self.plot.brp[1]:
                min_x = max(self.x1, self.plot.tlp[0] + 2)
                max_x = min(self.x2, self.plot.brp[0] - 2)
            else:
                self.drawing = False
                return
            if min_x > max_x:
                self.drawing = False
            else:
                self.drawing = True
                self.point1 = ScreenPoint(self.plot, min_x, self.y(min_x), self.color)
                self.point2 = ScreenPoint(self.plot, max_x, self.y(max_x), self.color)
        else:
            self.k = 'inf'
            self.b = None
            self.y1 = min(p1.y, p2.y)
            self.y2 = max(p1.y, p2.y)
            min_y = max(self.y1, self.plot.tlp[1] + 2)
            max_y = min(self.y2, self.plot.brp[1] - 2)
            if min_y <= max_y and self.plot.tlp[0] < p1.x < self.plot.brp[0]:
                self.drawing = True
                self.point1 = ScreenPoint(self.plot, p1.x, min_y, self.color)
                self.point2 = ScreenPoint(self.plot, p1.x, max_y, self.color)
            else:
                self.drawing = False

    def draw(self):
        if self.drawing:
            self.plot.draw_segment(self, self.color)

    def draw_qt(self, color=None, thickness=-1):
        if thickness == -1:
            thickness = self.thickness
        if color is None:
            color = self.color
        if self.drawing:
            self.plot.draw_segment(self.p1.tuple(), self.p2.tuple(), color, thickness, self.line_type)

    def y(self, x):
        return self.k * x + self.b

    def x(self, y):
        return (y - self.b) / self.k

    def move(self, x, y):
        self.p1.x += x
        self.p1.y += y
        self.p2.x += x
        self.p2.y += y
        if self.k == 'inf':
            self.y1 += y
            self.y2 += y
            min_y = max(self.y1, self.plot.tlp[1] + 2)
            max_y = min(self.y2, self.plot.brp[1] - 2)
            if min_y <= max_y and self.plot.tlp[0] < self.p1.x < self.plot.brp[0]:
                self.drawing = True
                self.point1 = ScreenPoint(self.plot, self.p1.x, min_y, self.color)
                self.point2 = ScreenPoint(self.plot, self.p1.x, max_y, self.color)
            else:
                self.drawing = False
        else:
            self.b = self.p1.y - self.k * self.p1.x
            self.x1 += x
            self.x2 += x
            if self.k > 0:
                min_x = max(self.x1, self.plot.tlp[0] + 2, self.x(self.plot.tlp[1] + 2))
                max_x = min(self.x2, self.plot.brp[0] - 2, self.x(self.plot.brp[1] - 2))
            elif self.k < 0:
                min_x = max(self.x1, self.plot.tlp[0] + 2, self.x(self.plot.brp[1] - 2))
                max_x = min(self.x2, self.plot.brp[0] - 2, self.x(self.plot.tlp[1] + 2))
            elif self.plot.tlp[1] < self.p1.y < self.plot.brp[1]:
                min_x = max(self.x1, self.plot.tlp[0] + 2)
                max_x = min(self.x2, self.plot.brp[0] - 2)
            else:
                self.drawing = False
                return
            if min_x > max_x:
                self.drawing = False
            else:
                self.drawing = True
                self.point1 = ScreenPoint(self.plot, min_x, self.y(min_x), self.color)
                self.point2 = ScreenPoint(self.plot, max_x, self.y(max_x), self.color)
