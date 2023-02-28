import utils.maths.angem as ag
import utils.history.serializable as serializable

index = 0
alph = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
used_names = set()


class GeneralObject:
    def __init__(self, plot, ag_object=None, color=(0, 0, 0), name=None, xy_projection=None, xz_projection=None):
        self.ag_object = ag_object
        self.plot = plot
        self.color = color
        self.name = name

        self.generate_name()

        if xy_projection is None or xz_projection is None:
            self.xy_projection, self.xz_projection = self.projections()
        else:
            self.xy_projection = xy_projection
            self.xz_projection = xz_projection

    def draw(self):
        for el in self.xy_projection:
            el.draw()
        for el in self.xz_projection:
            el.draw()

    def draw_qt(self, selected=False):
        if selected:
            for el in self.xy_projection:
                el.draw_qt(color=(250, 30, 30), thickness=(el.thickness + 2))
            for el in self.xz_projection:
                el.draw_qt(color=(250, 30, 30), thickness=(el.thickness + 2))
        for el in self.xy_projection:
            el.draw_qt()
        for el in self.xz_projection:
            el.draw_qt()

    def projections(self):
        xy_projection = self.plot.pm.get_projection(self.ag_object, 'xy', self.color)
        if not isinstance(xy_projection, (tuple, list)):
            xy_projection = xy_projection,
        xz_projection = self.plot.pm.get_projection(self.ag_object, 'xz', self.color)
        if not isinstance(xz_projection, (tuple, list)):
            xz_projection = xz_projection,
        return xy_projection, xz_projection

    def update_projections(self):
        self.xy_projection, self.xz_projection = self.projections()

    def move(self, x, y):
        if isinstance(self.ag_object, ag.Line) or isinstance(self.ag_object, ag.Plane):
            self.update_projections()
            return
        for el in self.xy_projection:
            el.move(x, y)
        for el in self.xz_projection:
            el.move(x, y)

    def generate_name(self):
        if self.name == 'GENERATE':
            global index, alph
            while alph[index] not in used_names:
                self.name = alph[index]
                used_names.add(self.name)
                # TODO: check if all used
            index += 1
            index %= len(alph)

    def to_dict(self):
        def convert(obj):
            if isinstance(obj, int) or isinstance(obj, float):
                return obj
            if isinstance(obj, list) or isinstance(obj, tuple):
                return list(map(convert, obj))
            dct = obj.__dict__
            res = {'class': obj.__class__}
            for key in serializable.angem_objects[obj.__class__]:
                res[key] = convert(dct[key])
            return res

        return {'name': self.name, 'color': self.color, 'ag_object': convert(self.ag_object)}

    @staticmethod
    def from_dict(plot, dct):
        def unpack_ag_object(obj):
            if isinstance(obj, int) or isinstance(obj, float):
                return obj
            if isinstance(obj, list) or isinstance(obj, tuple):
                return list(map(unpack_ag_object, obj))
            if isinstance(obj, dict):
                return obj['class'](*[unpack_ag_object(obj[key]) for key in serializable.angem_objects[obj['class']]])

        return GeneralObject(plot, unpack_ag_object(dct['ag_object']), dct['color'], dct['name'])
