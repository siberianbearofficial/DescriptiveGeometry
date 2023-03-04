from utils.drawing.general_object import GeneralObject


class Layer:
    def __init__(self, plot, name='', hidden=False, color=None, thickness=2):
        self.plot = plot
        self.hidden = hidden
        self.color = color
        self.thickness = thickness
        self.objects = []
        self.name = name

        self.serializable = ['hidden', 'objects', 'name']

    def add_object(self, ag_object, color, history_record=True, **config):
        self.objects.append(GeneralObject(self.plot, ag_object, color, name='GENERATE', **config))
        self.plot.sm.update_intersections()
        if history_record:
            self.plot.hm.add_record('add_object', ag_object, color)

    def delete_object(self, index, history_record=True):
        if history_record:
            self.plot.hm.add_record('delete_object', self.objects[-1].ag_object, self.objects[-1].color)
        self.objects[index].destroy_name_bars()
        self.objects.pop(index)
        self.plot.sm.update_intersections()

    def draw(self):
        if not self.hidden:
            for obj in self.objects:
                obj.draw()

    def draw_qt(self):
        if not self.hidden:
            for obj in self.objects:
                obj.draw_qt()

    def update_projections(self):
        for obj in self.objects:
            obj.update_projections()

    def clear(self):
        for obj in self.objects:
            obj.destroy_name_bars()
        self.objects = []

    def move_objects(self, x, y):
        for obj in self.objects:
            obj.move(x, y)

    def to_dict(self):
        return {'name': self.name, 'hidden': self.hidden, 'objects': [obj.to_dict(True) for obj in self.objects]}

    @staticmethod
    def from_dict(dct, plot):
        layer = Layer(plot, dct['name'], dct['hidden'])
        layer.objects = [GeneralObject.from_dict(plot, el) for el in dct['objects']]
        return layer

    def set_name(self, name):
        self.name = name

    def set_hidden(self, hidden):
        self.hidden = hidden
        if hidden:
            for el in self.objects:
                el.hide_name_bars()
        else:
            for el in self.objects:
                el.show_name_bars()
        self.plot.update()

    def replace_object(self, index, dct):
        self.objects[index].destroy_name_bars()
        self.objects[index] = GeneralObject.from_dict(self.plot, dct)
        self.plot.sm.update_intersections()
