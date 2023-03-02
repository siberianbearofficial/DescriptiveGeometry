from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtCore import Qt, pyqtSignal

from utils.drawing.screen_point import ScreenPoint, ScreenPoint2
from utils.drawing.screen_segment import ScreenSegment
from utils.drawing.screen_circle import ScreenCircle

from utils.drawing.axis import Axis
from utils.drawing.projections import ProjectionManager
from utils.drawing.history import HistoryManager
import utils.drawing.snap as snap
from utils.drawing.layer import Layer
import utils.drawing.drawing_on_plot as drw
from random import randint

drawing_functions = {
    'point': drw.create_point, 'segment': drw.create_segment, 'line': drw.create_line, 'plane': drw.create_plane,
    'perpendicular_segment': drw.create_perpendicular_segment, 'parallel_segment': drw.create_parallel_segment,
    'perpendicular_line': drw.create_perpendicular_line, 'parallel_line': drw.create_parallel_line,
    'plane_3p': drw.create_plane_3p, 'parallel_plane': drw.create_parallel_plane,
    'horizontal': drw.create_horizontal, 'frontal': drw.create_frontal,
    'distance': drw.get_distance, 'angle': drw.get_angle, 'circle': drw.create_circle, 'sphere': drw.create_sphere,
    'cylinder': drw.create_cylinder, 'cone': drw.create_cone, 'tor': drw.create_point, 'spline': drw.create_spline,
    'rotation_surface': drw.create_rotation_surface, 'intersection': drw.get_intersection}


class Plot(QWidget):
    objectSelected = pyqtSignal(object)
    printToCommandLine = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        self.setGeometry(159, 20, 711, 601)

        self.setStyleSheet("border-radius: 10px;")
        self.setObjectName("plot")

        self.screen = parent
        self.painter = QPainter()

        self.bg_color = (255, 255, 255)

        self.tlp = 0, 0
        self.brp = self.width(), self.height()
        self.zoom = 1
        self.zoom_step = 1.5
        self.camera_pos = (0, 0)

        self.layers = [Layer(self, 'Слой 1')]
        self.current_layer = 0
        self.selected_object = None
        self.selected_object_index = None

        self.axis = Axis(self)
        self.pm = ProjectionManager(self)
        self.sm = snap.SnapManager(self)
        self.hm = HistoryManager(self)

        self.clear()
        self.moving_camera = False
        self.mouse_pos = 0, 0
        self.extra_objects = tuple()
        self.i = 0

        self.serializable = ['bg_color', 'layers', 'current_layer']
        self.show()

        self.mouse_move = None
        self.mouse_left = None
        self.mouse_right = None
        self.enter = None
        self.esc = None

    def paintEvent(self, e):
        self.painter.begin(self)

        self.painter.setBackground(QColor(*self.bg_color))
        self.painter.setBackgroundMode(Qt.OpaqueMode)
        self.painter.fillRect(*self.tlp, *self.brp, QColor(*self.bg_color))

        self.axis.draw_qt()
        for layer in self.layers:
            layer.draw_qt()
        for obj in self.extra_objects:
            obj.draw_qt()
        if self.selected_object is not None:
            self.selected_object.draw_qt(selected=True)
        self.painter.end()

    def keyPressEvent(self, a0):
        key = a0.key()
        if key == Qt.Key_Escape:
            if self.esc is not None:
                self.esc(a0)
        if key == Qt.Key_Space:
            print('Enter')
            if self.enter is not None:
                self.enter(a0)
        elif key == Qt.Key_Delete and self.selected_object is not None:
            self.layers[self.selected_object_index[0]].delete_object(self.selected_object_index[1])
            self.selected_object_index, self.selected_object = None, None
            self.update()
        elif key == Qt.Key_C:
            self.draw('cylinder')
        elif key == Qt.Key_P:
            self.draw('point')
        elif key == Qt.Key_S:
            self.draw('segment')
        elif key == Qt.Key_O:
            self.draw('plane')
        elif key == Qt.Key_L:
            self.draw('line')
        elif key == Qt.Key_W:
            self.draw('perpendicular_segment')
        elif key == Qt.Key_E:
            self.draw('parallel_segment')
        elif key == Qt.Key_G:
            self.draw('perpendicular_line')
        elif key == Qt.Key_T:
            self.draw('parallel_line')
        elif key == Qt.Key_I:
            self.draw('plane_3p')
        elif key == Qt.Key_U:
            self.draw('parallel_plane')
        elif key == Qt.Key_H:
            self.draw('horizontal')
        elif key == Qt.Key_F:
            self.draw('frontal')
        elif key == Qt.Key_D:
            self.draw('distance')
        elif key == Qt.Key_A:
            self.draw('angle')
        elif key == Qt.Key_V:
            self.draw('circle')
        elif key == Qt.Key_B:
            self.draw('sphere')
        elif key == Qt.Key_K:
            self.draw('cone')
        elif key == Qt.Key_X:
            self.draw('intersection')
        elif key == Qt.Key_Q:
            self.draw('spline')
        elif key == Qt.Key_R:
            self.draw('rotation_surface')

    def draw_segment(self, p1, p2, color=(0, 0, 0), thickness=1, line_type=1):
        self.set_pen(color, thickness, line_type)
        self.painter.drawLine(*p1, *p2)

    def draw_point(self, point, color=(0, 0, 0), thickness=1):
        if self.tlp[0] + 1 <= point[0] <= self.brp[0] - 1 and self.tlp[1] + 1 <= point[1] <= self.brp[1] - 1:
            self.set_pen(color, thickness)
            self.painter.setBrush(QColor(*self.bg_color))
            self.painter.drawEllipse(point[0] - 5, point[1] - 5, 10, 10)

    def draw_point2(self, point, color=(0, 0, 0), thickness=1):
        if self.tlp[0] <= point[0] <= self.brp[0] and self.tlp[1] <= point[1] <= self.brp[1]:
            self.set_pen(color, thickness)
            self.painter.drawPoint(*point)

    def draw_circle(self, center, radius, color=(0, 0, 0), thickness=2):
        self.set_pen(color, thickness)
        self.painter.drawEllipse(center[0] - radius, center[1] - radius, radius * 2, radius * 2)
        # self.painter.setPen(QColor(*color))
        # self.painter.drawEllipse(*center, radius, radius)
        # if self.tlp[0] + radius <= center[0] <= self.brp[0] - radius \
        #         and self.tlp[1] + radius + 1 <= center[1] <= self.brp[1] - radius:

    def set_pen(self, color, thickness, line_type=1):
        self.painter.setPen(QPen(QColor(*color), thickness, line_type))

    def clear(self, index=-1):
        if index == -1:
            for layer in self.layers:
                layer.clear()
        else:
            self.layers[index].clear()
            self.sm.update_intersections()
        self.update()

    def draw(self, figure):
        self.setMouseTracking(True)
        drawing_functions[figure](self, 1)

    def update(self, *objects) -> None:
        self.extra_objects = objects
        super(Plot, self).update()

    def resizeEvent(self, a0) -> None:
        self.tlp = 0, 0
        self.brp = self.size().width(), self.size().height()
        self.axis.update(self)
        for layer in self.layers:
            layer.update_projections()
        self.update()

    def move_camera(self, x, y, update=True):
        x = int(x)
        y = int(y)
        self.axis.move(0, y)
        self.camera_pos = self.camera_pos[0] + x, self.camera_pos[1] + y
        self.pm.camera_pos = self.camera_pos
        if update:
            for layer in self.layers:
                layer.move_objects(x, y)
                # layer.update_projections()
            self.sm.update_intersections()
            self.update()

    def add_object(self, ag_object, color=None, end=False):
        if color is None:
            color = self.random_color()
        self.layers[self.current_layer].add_object(ag_object, color, history_record=True)
        self.update()
        if end:
            self.end()

    def delete_selected(self):
        print(str(self.selected_object), 'is near to be deleted! Please, don\'t do it!')

    def mousePressEvent(self, a0) -> None:
        if a0.button() == 1:
            print('mouse left')
            if self.mouse_left:
                self.mouse_left(a0.pos())
            else:
                self.select_object((a0.x(), a0.y()))
        elif a0.button() == 2:
            if self.mouse_right:
                self.mouse_right(a0.pos())
            else:
                self.mouse_pos = a0.x(), a0.y()
                self.moving_camera = True
        elif a0.button() == Qt.MouseButton.MidButton:
            self.mouse_pos = a0.x(), a0.y()
            self.moving_camera = True

    def mouseReleaseEvent(self, a0) -> None:
        if a0.button() in (2, Qt.MouseButton.MidButton):
            self.moving_camera = False

    def mouseMoveEvent(self, a0) -> None:
        # print('mouse move')
        if self.moving_camera:
            self.move_camera(a0.x() - self.mouse_pos[0], a0.y() - self.mouse_pos[1])
            self.mouse_pos = a0.x(), a0.y()
        if self.mouse_move:
            self.mouse_move(a0.pos())

    def wheelEvent(self, a0) -> None:
        if a0.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def select_object(self, pos):
        old_obj = self.selected_object
        self.selected_object, self.selected_object_index = None, None
        for i in range(len(self.layers)):
            if self.layers[i].hidden:
                continue
            for j in range(len(self.layers[i].objects)):
                obj = self.layers[i].objects[j]
                # TODO: избавиться от копипаста
                for el in obj.xy_projection:
                    if isinstance(el, ScreenPoint) and snap.distance(pos, el.tuple()) <= 7:
                        if obj != old_obj:
                            self.selected_object, self.selected_object_index = obj, (i, j)
                        break
                    if isinstance(el, ScreenPoint2) and snap.distance(pos, el.tuple()) <= 3:
                        if obj != old_obj:
                            self.selected_object, self.selected_object_index = obj, (i, j)
                        break
                    if isinstance(el, ScreenSegment) and snap.distance(pos, snap.nearest_point(pos, el)) <= 3:
                        if obj != old_obj:
                            self.selected_object, self.selected_object_index = obj, (i, j)
                        break
                    if isinstance(el, ScreenCircle) and abs(snap.distance(pos, el.center) - el.radius) <= 3:
                        if obj != old_obj:
                            self.selected_object, self.selected_object_index = obj, (i, j)
                        break
                for el in obj.xz_projection:
                    if isinstance(el, ScreenPoint) and snap.distance(pos, el.tuple()) <= 7:
                        if obj != old_obj:
                            self.selected_object, self.selected_object_index = obj, (i, j)
                        break
                    if isinstance(el, ScreenPoint2) and snap.distance(pos, el.tuple()) <= 2:
                        if obj != old_obj:
                            self.selected_object, self.selected_object_index = obj, (i, j)
                        break
                    if isinstance(el, ScreenSegment) and snap.distance(pos, snap.nearest_point(pos, el)) <= 2:
                        if obj != old_obj:
                            self.selected_object, self.selected_object_index = obj, (i, j)
                        break
                    if isinstance(el, ScreenCircle) and abs(snap.distance(pos, el.center) - el.radius) <= 3:
                        if obj != old_obj:
                            self.selected_object, self.selected_object_index = obj, (i, j)
                        break
        if self.selected_object is not None:
            self.objectSelected.emit(self.selected_object)
        self.update()

    def zoom_in(self, pos=None):
        if pos is None:
            pos = (self.tlp[0] + self.brp[0]) // 2, (self.tlp[1] + self.brp[1]) // 2
        self.zoom *= self.zoom_step
        self.pm.zoom *= self.zoom_step
        self.move_camera((self.zoom_step - 1) * ((self.axis.rp[0] - pos[0]) + self.camera_pos[0]),
                         (self.zoom_step - 1) * (self.axis.rp[1] - pos[1]), update=False)
        for layer in self.layers:
            layer.update_projections()
        self.sm.update_intersections()
        self.update()

    def zoom_out(self, pos=None):
        if pos is None:
            pos = (self.tlp[0] + self.brp[0]) // 2, (self.tlp[1] + self.brp[1]) // 2
        self.zoom /= self.zoom_step
        self.pm.zoom /= self.zoom_step
        new_camera_x = (self.camera_pos[0] + self.axis.rp[0] - pos[0]) / self.zoom_step - self.axis.rp[0] + pos[0]
        new_axis_y = pos[1] - (pos[1] - self.axis.lp[1]) / self.zoom_step
        self.move_camera(new_camera_x - self.camera_pos[0], new_axis_y - self.axis.lp[1], update=False)
        for layer in self.layers:
            layer.update_projections()
        self.sm.update_intersections()
        self.update()

    def end(self):
        self.mouse_move = None
        self.mouse_left = None
        self.mouse_right = None
        self.setMouseTracking(False)
        self.update()

    def print(self, s):
        self.printToCommandLine.emit(s)
        print(s)

    @staticmethod
    def random_color():
        red = randint(20, 240)
        green = randint(20, 240)
        blue = randint(20, min(570 - red - green, 240))
        return red, green, blue
        while True:
            red = randint(20, 240)
            green = randint(20, 240)
            blue = randint(20, 570 - red - green)
            if 300 < red + green + blue < 570:
                return red, green, blue


def main():
    app = QApplication([])
    plot = Plot(None)
    app.exec_()


if __name__ == '__main__':
    main()
