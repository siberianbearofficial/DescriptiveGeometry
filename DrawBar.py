from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt
from DrawTool import DrawTool
from widget import Widget


class DrawBar(Widget):
    def __init__(self, parent, *names):
        super().__init__(parent)

        self.setStyleSheet("background-color: #EAEAEA;\n"
                           "border-radius: 10px;")

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setAlignment(Qt.AlignTop)

        self.tools = list()

        for name in names:
            draw_tool = DrawTool(name, self.central_widget)
            self.tools.append(draw_tool)
            self.layout.addWidget(draw_tool)

    def set_images(self, *images):
        pass

    def set_on_click_listeners(self, *funcs):
        for i in range(len(funcs)):
            self.tools[i].set_on_click_listener(funcs[i])
        return self
