import math
from math import radians

import numpy as np
import torch
import torch.nn.functional as F
import torchvision
from PIL import Image
from cv2 import cv2
from numpy.random.mtrand import random_integers


class ToTensor(object):
    """Convert ndarrays from given sample to Tensors."""

    def __call__(self, sample):
        """
        :param sample: Sample consisting of image and annotation
        :return: Transposed GERALD sample as tensor
        """
        im, targets, idx = sample
        del sample

        # Swap color axis because
        # numpy image: H x W x C
        # torch image: C X H X W
        new_im = im.transpose((2, 0, 1))
        return torch.from_numpy(new_im.copy()).type(torch.FloatTensor), targets, idx


class Rescale(object):
    """Rescale the image in a sample to a given size.

    Args:
        output_size (tuple or int): Desired output size. If tuple, output is
            matched to output_size. If int, smaller of image edges is matched
            to output_size keeping aspect ratio the same.
    """

    def __init__(self, output_size, is_tensor=False):
        assert isinstance(output_size, (int, tuple))
        self.output_size = output_size
        self.is_tensor = is_tensor

    def __call__(self, sample):
        im, targets, idx = sample

        if self.is_tensor:
            h, w = im.shape[2:]
        else:
            h, w = im.shape[:2]

        # Calculate new image size
        if isinstance(self.output_size, int):
            if h > w:  # Given output size is int, smaller edge is taken as reference for new size
                new_w, new_h = self.output_size, self.output_size * h / w
            else:
                new_w, new_h = self.output_size * w / h, self.output_size,
        else:
            new_w, new_h = self.output_size

        new_w, new_h = int(new_w), int(new_h)

        # Resize image and bounding boxes
        if self.is_tensor:
            new_im = F.interpolate(im, size=self.output_size[::-1])
        else:
            new_im = cv2.resize(im, (new_w, new_h))

        new_targets = torch.zeros(targets.shape, dtype=torch.float)

        new_targets[:, 0] = (targets[:, 0] * new_w / w).round()
        new_targets[:, 1] = (targets[:, 1] * new_h / h).round()
        new_targets[:, 2] = torch.clamp((targets[:, 2] * new_w / w), 1, new_w)  # Make sure width/height or never 0
        new_targets[:, 3] = torch.clamp((targets[:, 3] * new_h / h), 1, new_h)
        new_targets[:, 4:] = targets[:, 4:]
        new_targets[:, 5:] = targets[:, 5:]

        del im, targets, sample

        return new_im, new_targets, idx


class Rotate(object):
    def __init__(self, angle=0):
        assert angle in (0, 90, 180, 270), "Angle has to be 0, 90, 180, 270"
        self.angle = angle

    def __call__(self, sample):
        im, targets, idx = sample
        new_targets = torch.zeros(targets.shape, dtype=torch.float)

        if self.angle == 0:  # 0 degrees rotation
            return sample
        elif self.angle == 90:  # 90 degrees rotation
            new_im = np.rot90(im, k=1)
            h, w = new_im.shape[:2]

            new_targets[:, 0:2] = self.rotate_points(targets[:, 0:2], angle=radians(-90), round_output=True)
            new_targets[:, 1] += h

            new_targets[:, 2] = targets[:, 3]
            new_targets[:, 3] = targets[:, 2]
        elif self.angle == 180:  # 180 degrees rotation
            new_im = np.rot90(im, k=2)
            h, w = new_im.shape[:2]

            new_targets[:, 0:2] = self.rotate_points(targets[:, 0:2], angle=radians(-180), round_output=True)
            new_targets[:, 0] += w
            new_targets[:, 1] += h

            new_targets[:, 2] = targets[:, 2]
            new_targets[:, 3] = targets[:, 3]
        elif self.angle == 270:  # 270 degrees rotation / or -90
            new_im = np.rot90(im, k=3)
            h, w = new_im.shape[:2]

            new_targets[:, 0:2] = self.rotate_points(targets[:, 0:2], angle=radians(-270), round_output=True)
            new_targets[:, 0] += w

            new_targets[:, 2] = targets[:, 3]
            new_targets[:, 3] = targets[:, 2]
        else:
            raise ValueError("Rotation should be 0, 90, 180, or 270 degrees")

        new_targets[:, 4:] = targets[:, 4:]
        new_targets[:, 5:] = targets[:, 5:]

        del im, targets, sample
        return new_im, new_targets, idx

    @staticmethod
    def rotate_points(points: torch.Tensor, angle=0.0, round_output=False):
        """
        Rotates a tensor of x,y coordinates with given angle
        :param points: Nx2 Tensor
        :param angle: Rotation angle
        :param round_output: If True rounds output to int
        :return: Nx2 Tensor with rotated points
        """
        rot_tensor = torch.tensor([[math.cos(angle), -math.sin(angle)],
                                   [math.sin(angle), math.cos(angle)]], dtype=torch.float)
        rot_points = rot_tensor @ points.t()
        if round_output:
            return rot_points.t().round()
        else:
            return rot_points.t()


class Flip(object):
    def __init__(self, kind="ud"):
        assert kind in ("ud", "lr"), "Kind has to be ud (up-down) or lr (left-right)"
        self.kind = kind

    def __call__(self, sample):
        im, targets, idx = sample
        new_targets = torch.zeros(targets.shape, dtype=torch.float)

        h, w = im.shape[:2]
        if self.kind == "ud":
            new_im = np.flipud(im)
            new_targets[:, 0] = targets[:, 0]
            new_targets[:, 1] = h - targets[:, 1]

        elif self.kind == "lr":
            new_im = np.fliplr(im)
            new_targets[:, 0] = w - targets[:, 0]
            new_targets[:, 1] = targets[:, 1]
        else:
            raise ValueError("Flip has to be of kind up-down or left-right")

        new_targets[:, 2:] = targets[:, 2:]

        del im, targets

        return new_im, new_targets, idx


class GaussianNoise(object):
    def __init__(self, mean=0., std=1.):
        self.std = std
        self.mean = mean

    def __call__(self, sample):
        im, targets, idx = sample

        if type(im) == np.ndarray:
            new_im = im + np.random.random_sample(im.shape) * self.std + self.mean
        elif type(im) == torch.tensor:
            new_im = im + torch.randn(im.size()) * self.std + self.mean
        else:
            raise ValueError("Type %s not supported for adding gaussian noise" % str(type(im)))
        del im
        return new_im, targets, idx


class ColorJitter(object):
    """
    Applies random color jitter to image
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, sample):
        im, targets, idx = sample

        pil_im = Image.fromarray((im * 255).astype(np.uint8))
        color_jitter = torchvision.transforms.ColorJitter(**self.kwargs)
        new_im = color_jitter(pil_im)
        new_im = np.array(new_im) / 255

        del im, sample

        return new_im, targets, idx


class CenterCrop(object):
    """
    Takes a center crop if the image
    """

    def __init__(self, factor=0.25, tol=2, is_tensor=False):
        """

        :param factor: Crop factor
        :param tol: Tolerance between target borders and image borders
        """
        self.factor = factor
        self.tol = tol
        self.is_tensor = is_tensor

    def __call__(self, sample):
        im, targets, idx = sample

        if self.is_tensor:
            h, w = im.shape[2:]
        else:
            h, w = im.shape[:2]

        self.size = (int(w * self.factor), int(h * self.factor))

        x_c = int(w / 2)
        y_c = int(h / 2)

        if self.is_tensor:
            new_im = im[:, :, y_c - int(self.size[1] / 2): y_c + int(self.size[1] / 2),
                     x_c - int(self.size[0] / 2): x_c + int(self.size[0] / 2)]
        else:
            new_im = im[y_c - int(self.size[1] / 2): y_c + int(self.size[1] / 2),
                     x_c - int(self.size[0] / 2): x_c + int(self.size[0] / 2)]

        crop_targets = torch.zeros(targets.shape, dtype=torch.float)
        crop_targets[:, 0] = targets[:, 0] - int((w - self.size[0]) / 2)
        crop_targets[:, 1] = targets[:, 1] - int((h - self.size[1]) / 2)
        crop_targets[:, 2:] = targets[:, 2:]

        # Remove targets outside image
        xyxy_targets = torch.zeros(targets.shape, dtype=torch.float)
        xyxy_targets[:, 0] = crop_targets[:, 0] - crop_targets[:, 2] / 2
        xyxy_targets[:, 1] = crop_targets[:, 1] - crop_targets[:, 3] / 2
        xyxy_targets[:, 2] = crop_targets[:, 0] + crop_targets[:, 2] / 2
        xyxy_targets[:, 3] = crop_targets[:, 1] + crop_targets[:, 3] / 2

        xyxy_targets[:, 0] = torch.clamp(xyxy_targets[:, 0], self.tol, self.size[0] - self.tol)
        xyxy_targets[:, 1] = torch.clamp(xyxy_targets[:, 1], self.tol, self.size[1] - self.tol)
        xyxy_targets[:, 2] = torch.clamp(xyxy_targets[:, 2], self.tol, self.size[0] - self.tol)
        xyxy_targets[:, 3] = torch.clamp(xyxy_targets[:, 3], self.tol, self.size[1] - self.tol)

        xyxy_targets[:, 4:] = crop_targets[:, 4:]

        xyxy_targets = xyxy_targets[xyxy_targets[:, 0] != xyxy_targets[:, 2]]
        xyxy_targets = xyxy_targets[xyxy_targets[:, 1] != xyxy_targets[:, 3]]

        new_targets = torch.zeros(xyxy_targets.shape, dtype=torch.float)  # Back to xc, yc, w, h
        new_targets[:, 0] = torch.round((xyxy_targets[:, 0] + xyxy_targets[:, 2]) / 2)
        new_targets[:, 1] = torch.round((xyxy_targets[:, 1] + xyxy_targets[:, 3]) / 2)
        new_targets[:, 2] = torch.floor(xyxy_targets[:, 2] - xyxy_targets[:, 0])
        new_targets[:, 3] = torch.floor(xyxy_targets[:, 3] - xyxy_targets[:, 1])
        new_targets[:, 4:] = xyxy_targets[:, 4:]

        del im, targets, crop_targets, xyxy_targets, sample

        return new_im, new_targets, idx


class RandomCrop(object):
    """
    Takes a random crop of the image
    """

    def __init__(self, min_size=(300, 100), max_size=(1000, 600), tol=2):
        assert isinstance(min_size, (int, tuple)), "Size has to be either int or tuple type"
        assert isinstance(max_size, (int, tuple)), "Size has to be either int or tuple type"

        if isinstance(min_size, int):
            self.min_size = (min_size, min_size)
        else:
            self.min_size = min_size

        if isinstance(max_size, int):
            self.max_size = (max_size, max_size)
        else:
            self.max_size = max_size

        if isinstance(min_size, int) and isinstance(max_size, int):
            r = random_integers(self.min_size[0], self.max_size[0])
            self.size = (r, r)
        else:
            self.size = (random_integers(self.min_size[0], self.max_size[0]),
                         random_integers(self.min_size[1], self.max_size[1]))

        self.tol = tol

    def __call__(self, sample, keep_aspect=True):
        im, targets, idx = sample

        h, w = im.shape[:2]

        if keep_aspect:
            aspect = w / h
            if aspect >= 1:
                self.size = (int(self.size[0] * aspect), self.size[1])
            else:
                self.size = (self.size[0], int(self.size[1] * aspect))

        assert self.size[0] <= w, "Max width must be smaller than image width"
        assert self.size[1] <= h, "Max height must be smaller than image width"

        while True:
            top = np.random.randint(0, h - self.size[1])
            left = np.random.randint(0, w - self.size[0])

            new_im = im[top: top + self.size[1], left: left + self.size[0]]

            crop_targets = torch.zeros(targets.shape, dtype=torch.float)
            crop_targets[:, 0] = targets[:, 0] - left
            crop_targets[:, 1] = targets[:, 1] - top
            crop_targets[:, 2:] = targets[:, 2:]

            # Remove targets outside image
            xyxy_targets = torch.zeros(targets.shape, dtype=torch.float)
            xyxy_targets[:, 0] = crop_targets[:, 0] - crop_targets[:, 2] / 2
            xyxy_targets[:, 1] = crop_targets[:, 1] - crop_targets[:, 3] / 2
            xyxy_targets[:, 2] = crop_targets[:, 0] + crop_targets[:, 2] / 2
            xyxy_targets[:, 3] = crop_targets[:, 1] + crop_targets[:, 3] / 2

            xyxy_targets[:, 0] = torch.clamp(xyxy_targets[:, 0], self.tol, self.size[0] - self.tol)
            xyxy_targets[:, 1] = torch.clamp(xyxy_targets[:, 1], self.tol, self.size[1] - self.tol)
            xyxy_targets[:, 2] = torch.clamp(xyxy_targets[:, 2], self.tol, self.size[0] - self.tol)
            xyxy_targets[:, 3] = torch.clamp(xyxy_targets[:, 3], self.tol, self.size[1] - self.tol)

            xyxy_targets[:, 4:] = crop_targets[:, 4:]

            xyxy_targets = xyxy_targets[xyxy_targets[:, 0] != xyxy_targets[:, 2]]
            xyxy_targets = xyxy_targets[xyxy_targets[:, 1] != xyxy_targets[:, 3]]

            new_targets = torch.zeros(xyxy_targets.shape, dtype=torch.float)  # Back to xc, yc, w, h
            new_targets[:, 0] = torch.round((xyxy_targets[:, 0] + xyxy_targets[:, 2]) / 2)
            new_targets[:, 1] = torch.round((xyxy_targets[:, 1] + xyxy_targets[:, 3]) / 2)
            new_targets[:, 2] = torch.floor(xyxy_targets[:, 2] - xyxy_targets[:, 0])
            new_targets[:, 3] = torch.floor(xyxy_targets[:, 3] - xyxy_targets[:, 1])
            new_targets[:, 4:] = xyxy_targets[:, 4:]

            if len(new_targets) > 0:
                break

        del im, targets, crop_targets, xyxy_targets, sample

        return new_im, new_targets, idx
