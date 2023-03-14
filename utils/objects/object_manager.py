from utils.objects.layer import Layer
from random import randint
from utils.objects.general_object import GeneralObject


class ObjectManager:
    def __init__(self, func_plot_update, func_plot_obj, plot_full_update, func_history_record, func_object_selected):
        self.layers = [Layer("Layer 1")]
        self.current_layer = 0
        self.selected_object = None
        self.selected_object_index = None
        self.func_plot_update = func_plot_update
        self.func_plot_obj = func_plot_obj
        self.plot_full_update = plot_full_update
        self.func_history_record = func_history_record
        self.func_object_selected = func_object_selected

    def add_object(self, ag_object, name='', color=None, history_record=True, **config):
        if color is None:
            color = self.random_color()
        obj = GeneralObject(ag_object, color, name, **config)
        self.layers[self.current_layer].add_object(obj)
        self.func_plot_obj(obj.id, obj)
        self.func_plot_update()

    def find_by_id(self, id):
        for i in range(len(self.layers)):
            for j in range(len(self.layers[i].objects)):
                if self.layers[i].objects[j].id == id:
                    return i, j

    def delete_selected_object(self, history_record=True):
        if self.selected_object is None:
            return
        self.layers[self.selected_object_index[0]].delete_object(
            self.selected_object_index[1], history_record=history_record)
        self.func_plot_obj(self.selected_object.id, None)
        self.selected_object = None
        for func in self.func_object_selected:
            func(0)
        self.func_plot_update()

    def add_layer(self, name, hidden=False):
        self.layers.append(Layer(name, hidden))

    def select_object(self, id):
        if id == 0:
            self.selected_object = None
            self.selected_object_index = None
            for func in self.func_object_selected:
                func(0)
        else:
            self.selected_object_index = self.find_by_id(id)
            self.selected_object = self.layers[self.selected_object_index[0]].objects[self.selected_object_index[1]]
            for func in self.func_object_selected:
                func(self.selected_object.id)

    def sel_layer_hidden(self, ind, hidden):
        self.layers[ind].hidden = hidden
        self.plot_full_update(self.get_all_objects())

    def delete_layer(self, index, history_record=True):
        if history_record:
            self.func_history_record('delete_layer', self.layers[index].to_dict(), index)
        self.layers[index].clear()
        self.layers.pop(index)
        if self.current_layer >= index:
            self.current_layer -= 1
        self.plot_full_update(self.get_all_objects())

    def get_all_objects(self):
        for layer in self.layers:
            if layer.hidden:
                continue
            for obj in layer.objects:
                yield obj

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

    def set_layer_color(self, color, layer=None):
        if layer is None:
            layer = self.current_layer
        self.layers[layer].color = color

    def set_layer_name(self, name, layer=None):
        if layer is None:
            layer = self.current_layer
        self.layers[layer].name = name

    def set_layer_thickness(self, thickness, layer=None):
        if layer is None:
            layer = self.current_layer
        self.layers[layer].thickness = thickness

    def set_object_name(self, name, index=None):
        if index is None:
            index = self.selected_object_index
        self.layers[index[0]].objects[index[1]].name = name

    def set_object_color(self, color, index=None):
        if index is None:
            index = self.selected_object_index
        self.layers[index[0]].objects[index[1]].color = color

    def set_object_thickness(self, thickness, index=None):
        if index is None:
            index = self.selected_object_index
        self.layers[index[0]].objects[index[1]].thickness = thickness

    def set_object_ag_obj(self, dct, index=None):
        if index is None:
            index = self.selected_object_index
        self.layers[index[0]].objects[index[1]].ag_object = GeneralObject.from_dict(dct)

    def set_object_config(self, config, index=None):
        if index is None:
            index = self.selected_object_index
        self.layers[index[0]].objects[index[1]].config = config