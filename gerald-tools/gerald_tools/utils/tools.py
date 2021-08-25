from typing import List

import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt

from .labels import WeatherCondition, LightCondition, GERALDLabels


class BoundingBox:
    def __init__(self, x_min: int, y_min: int, x_max: int, y_max: int, label=GERALDLabels.Hp_0,
                 relevant=False, weather=None, light=None,
                 src_width=None, src_height=None, identifier=None):
        """
        Creates a bounding box element for signals
        :param identifier: Bounding boxes with same identifier show the same object (e.g. in different frames)
        :param src_width: Used to compute normalized coordinates
        :param src_height: Used to compute normalized coordinates
        :param x_min:
        :param y_min:
        :param x_max:
        :param y_max:
        :param label:
        :param relevant: If True, boundingbox was relevant in the scene
        """
        self.identifier = identifier
        self.label = label
        self.relevant = relevant
        self.weather = weather
        self.light = light

        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

        self.coords = np.array([self.x_min, self.y_min, self.x_max, self.y_max])

        self.x_c = round((self.x_max + self.x_min) / 2, 0)
        self.y_c = round((self.y_max + self.y_min) / 2, 0)
        self.w = self.x_max - self.x_min
        self.h = self.y_max - self.y_min

        self.src_width = src_width
        self.src_height = src_height

        # Coordinates and size normalized to image size
        if src_width is not None:
            self.x_min_nm = self.x_min / src_width
            self.x_max_nm = self.x_max / src_width

            self.x_c_nm = (self.x_max + self.x_min) / (2 * src_width)
            self.w_nm = (self.x_max - self.x_min) / src_width
        else:
            self.x_min_nm = None
            self.x_max_nm = None

            self.x_c_nm = None
            self.w_nm = None

        if src_height is not None:
            self.y_min_nm = self.y_min / src_height
            self.y_max_nm = self.y_max / src_height

            self.y_c_nm = (self.y_max + self.y_min) / (2 * src_height)
            self.h_nm = (self.y_max - self.y_min) / src_height
        else:
            self.y_min_nm = None
            self.y_max_nm = None

            self.y_c_nm = None
            self.h_nm = None

        if self.w_nm is not None and self.h_nm is not None:
            self.area_nm = self.w_nm * self.h_nm
        else:
            self.area_nm = None

        self.area = self.w * self.h

        self.aspect = self.w / self.h if self.h != 0 else None

    def rescale(self, new_size: tuple):
        """
        Rescales the bounding box to a new size
        :param new_size: tuple containing new_src_widthxnew_src_height
        :return:
        """
        if self.src_width in [0, None] or self.src_height in [0, None]:
            raise ValueError("Bounding Box has no valid source size")

        scale_w, scale_h = new_size[0] / self.src_width, new_size[1] / self.src_height

        self.x_min = int(round(self.x_min * scale_w, 0))
        self.y_min = int(round(self.y_min * scale_h, 0))
        self.x_max = int(round(self.x_max * scale_w, 0))
        self.y_max = int(round(self.y_max * scale_h, 0))

        self.coords = np.array([self.x_min, self.y_min, self.x_max, self.y_max])
        self.x_c = int(round((self.x_max + self.x_min) / 2, 0))
        self.y_c = int(round((self.y_max + self.y_min) / 2, 0))
        self.w = self.x_max - self.x_min
        self.h = self.y_max - self.y_min

        self.area = self.w * self.h
        self.src_width = new_size[0]
        self.src_height = new_size[1]

        return

    def __repr__(self):
        return "Label %s, x_c: %d, y_c: %d, w: %d, h: %d, ID: %s" % (str(self.label),
                                                                     self.x_c,
                                                                     self.y_c,
                                                                     self.w,
                                                                     self.h,
                                                                     str(self.identifier))


class Annotation:
    def __init__(self):
        self.src_height: int = 0
        self.src_width: int = 0
        self.src_depth: int = 0

        self.src_name: str = ""
        self.src_url: str = ""
        self.src_time: float = 0.0

        self.author: str = ""
        self.author_url: str = ""

        self.light = LightCondition.Unknown
        self.weather = WeatherCondition.Unknown

        self.hash = None
        self.objects: List[GroundTruthObject] = []
        self.n_targets = 0

    def __repr__(self):
        return "Annotation | " + self.src_name

    def __len__(self):
        return len(self.objects)

    def add_ground_truth_object(self, x_min, y_min, x_max, y_max, label, relevant):
        o = GroundTruthObject(x_min=x_min, y_min=y_min, x_max=x_max, y_max=y_max, label=label, relevant=relevant,
                              weather=self.weather, light=self.light,
                              src_width=self.src_width, src_height=self.src_height, annotation=self)
        self.objects.append(o)
        self.n_targets = len(self.objects)

    def get_all_object_coords(self):
        """
        Returns a nx4 ndarray containing all object coordinates
        :return:
        """
        return np.stack([o.coords for o in self.objects])


class GroundTruthObject(BoundingBox):

    def __init__(self, x_min=0, y_min=0, x_max=0, y_max=0, label=GERALDLabels.Hp_0, relevant=False,
                 weather=WeatherCondition.Unknown, light=LightCondition.Unknown,
                 src_width=0, src_height=0, annotation=None):
        """
        Creates a Ground Truth object
        :param x_min:
        :param y_min:
        :param x_max:
        :param y_max:
        :param label:
        :param relevant:
        :param src_width:
        :param src_height:
        """
        super(GroundTruthObject, self).__init__(x_min=x_min, y_min=y_min, x_max=x_max, y_max=y_max,
                                                label=label, relevant=relevant, weather=weather, light=light,
                                                src_width=src_width, src_height=src_height)

        self.annotation = annotation  # Reference to annotation that contains the bounding box
        self.hash = None

    def __repr__(self):
        return "Ground Truth Object | Label %s, x_c: %d, y_c: %d, w: %d, h: %d, ID: %s, Relevant: %s" % \
               (str(self.label.name), self.x_c, self.y_c, self.w, self.h,
                str(self.identifier), str(self.relevant))


def plot_targets_over_im(im, targets):
    fig, ax = plt.subplots()

    ax.imshow(im, interpolation='nearest')

    for obj in targets:
        x, y = obj[0] - obj[2] / 2, obj[1] - obj[3] / 2  # Coordinates of the lower left corner
        w, h = obj[2], obj[3]  # Object with height

        rect = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor='g', facecolor='none', clip_on=False)
        ax.add_patch(rect)
        print(obj)

    plt.show()
