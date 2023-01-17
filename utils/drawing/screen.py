from utils.drawing.command_line import CommandLine
from utils.drawing.plot import Plot
from utils.drawing.menu import Menu

import pygame as pg


class Screen:

    def __init__(self, width, height, title, serializer=None, bg_color=(200, 200, 200)):
        self.width = width
        self.height = height
        self.tlp = (0, 0)
        self.brp = (width, height)
        self.click_pos = None
        self.bg_color = bg_color
        self.serializer = serializer

        self.screen = pg.display.set_mode((width, height), pg.RESIZABLE)
        self.title = title
        pg.display.set_caption(title)

        self.screen.fill(self.bg_color)

        self.plot = Plot(self, (self.tlp[0] + 10, 70), (self.brp[0] - 10, self.brp[1] - 50))
        self.command_line = CommandLine(self)
        self.serializable = ['title', 'bg_color', 'plot']
        self.menu = Menu(self)

        self.menu.full_update_toolbars()

    def save(self):
        self.serializer.serialize(self)

    def load(self):
        self.serializer.deserialize(self)

    def update(self, title=None, bg_color=None):
        if title is not None:
            self.title = title
        if bg_color is not None:
            self.bg_color = bg_color
        pg.display.update()

    def clicked(self, event):
        self.click_pos = event.pos
        if event.button == 1:
            if self.menu.clicked_on(self.click_pos):
                return
            if self.command_line.clicked_on(self.click_pos):
                return
            # TODO: if clicked on plot
            self.plot.clicked(self.click_pos)
        elif event.button == 3:
            self.plot.moving_camera()
        elif event.button == 4:
            self.plot.zoom_in()
        elif event.button == 5:
            self.plot.zoom_out()

    def key_down(self, event):
        if event.key == 127 and self.plot.selected_object is not None:
            self.plot.layers[self.plot.selected_object_index[0]].delete_object(self.plot.selected_object_index[1])
        elif event.key == 1073741906:
            self.plot.move_camera(0, 5)
        elif event.key == 1073741904:
            self.plot.move_camera(5, 0)

    def resize(self, width, height):
        self.screen = pg.display.set_mode((width, height), pg.RESIZABLE)
        self.screen.fill(self.bg_color)
        self.width = width
        self.height = height
        self.tlp = (0, 0)
        self.brp = (width, height)
        self.plot.resize((self.tlp[0] + 10, 70), (self.brp[0] - 10, self.brp[1] - 50))
        self.menu.full_update_toolbars()
        self.command_line.update()
