import json
import logging
import os
import random
import xml.etree.ElementTree as ET
from cv2 import cv2
from typing import List
from torch.utils.data import Dataset
from torchvision.transforms import transforms, ColorJitter

import numpy as np
import torch
from imagehash import ImageHash
from tqdm.auto import tqdm

from . import GaussianNoise, ToTensor, Flip
from .utils import Annotation, GERALDLabels, WeatherCondition, LightCondition


class GERALDDataset(Dataset):
    annotations: List[Annotation] = None

    def __init__(self, path: str, transform=None, subset="all", shuffle=True,
                 random_augment=True, im_input_size=(512, 512), split=0.8, test=0.1):
        """
        Dataset class for pytorch use-cases
        :param path: Path to the GERALD dataset
        :param transform: Additional transformation
        :param subset: Subset of GERALD (e.g. "all", "val", "train", "test", "sunny" etc)
        :param shuffle: Shuffles the files
        :param random_augment: Randomly augment images after loading
        :param im_input_size: input size for e.g. a neural network
        :param split: split ratio for training and validation data
        :param test: percentage of data used for testing
        """
        logging.info("Initializing GERALD Dataset")
        logging.info("Using " + subset + " subset")
        logging.info("Loading from: %s" % path)

        self.path = path

        with open(self.path + '/info.json', 'r') as fp:
            self.infos = json.load(fp)

        self.subset = subset
        self.labels = GERALDLabels
        self.im_path = self.path + "/JPEGImages/"
        self.an_path = self.path + "/Annotations/"

        self.split = split  # Train/val split
        self.test = test  # Percentage of test data

        self.model_input_size = im_input_size

        logging.info("Model input size: %s" % str(self.model_input_size))

        self.random_augment = random_augment
        self.transform = transform
        self.filenames = self.get_all_filenames()
        self.n_images = len(self.filenames)

        self.n_train_images = round(self.split * self.n_images)
        self.n_val_images = round((1 - self.split) * self.n_images)
        self.n_test_images = round(self.test * self.n_images)
        self.n_classes = len(GERALDLabels)

        if shuffle:  # Use fixed seed for constant shuffle
            random.seed(331297)
            random.shuffle(self.filenames)

        logging.info("Total number of images: %5d" % len(self.filenames))
        logging.info("Number of train images: %5d" % self.n_train_images)
        logging.info("Number of validation images: %5d" % self.n_val_images)
        logging.info("Number of test of images: %5d" % self.n_test_images)
        logging.info("Use random data augmentation: " + str(self.random_augment))

        if not self.annotations:  # Load all annotations
            GERALDDataset.annotations = self.import_xml_annotations(self.filenames)

        if self.subset == "train":
            self.subset_filenames = self.filenames[:self.n_train_images]
            self.subset_annotations = self.annotations[:self.n_train_images]
            logging.info("Signals in the train subset:")
        elif self.subset == "val":
            self.subset_filenames = self.filenames[self.n_train_images:]
            self.subset_annotations = self.annotations[self.n_train_images:]
            logging.info("Signals in the val subset:")
        elif self.subset == "val_sunny":
            self.subset_filenames = self.filenames[self.n_train_images:]
            self.subset_annotations = self.annotations[self.n_train_images:]

            idxs = [i for i, an in enumerate(self.subset_annotations) if an.weather == WeatherCondition.Sunny]
            self.subset_filenames = [fn for i, fn in enumerate(self.subset_filenames) if i in idxs]
            self.subset_annotations = [an for i, an in enumerate(self.subset_annotations) if i in idxs]

            logging.info("Signals in the val (sunny) subset:")
        elif self.subset == "val_cloudy":
            self.subset_filenames = self.filenames[self.n_train_images:]
            self.subset_annotations = self.annotations[self.n_train_images:]

            idxs = [i for i, an in enumerate(self.subset_annotations) if an.weather == WeatherCondition.Cloudy]
            self.subset_filenames = [fn for i, fn in enumerate(self.subset_filenames) if i in idxs]
            self.subset_annotations = [an for i, an in enumerate(self.subset_annotations) if i in idxs]

            logging.info("Signals in the val (cloudy) subset:")
        elif self.subset == "val_rainy":
            self.subset_filenames = self.filenames[self.n_train_images:]
            self.subset_annotations = self.annotations[self.n_train_images:]

            idxs = [i for i, an in enumerate(self.subset_annotations) if an.weather == WeatherCondition.Rainy]
            self.subset_filenames = [fn for i, fn in enumerate(self.subset_filenames) if i in idxs]
            self.subset_annotations = [an for i, an in enumerate(self.subset_annotations) if i in idxs]

            logging.info("Signals in the val (rainy) subset:")
        elif self.subset == "val_foggy":
            self.subset_filenames = self.filenames[self.n_train_images:]
            self.subset_annotations = self.annotations[self.n_train_images:]

            idxs = [i for i, an in enumerate(self.subset_annotations) if an.weather == WeatherCondition.Foggy]
            self.subset_filenames = [fn for i, fn in enumerate(self.subset_filenames) if i in idxs]
            self.subset_annotations = [an for i, an in enumerate(self.subset_annotations) if i in idxs]

            logging.info("Signals in the val (foggy) subset:")
        elif self.subset == "val_snowy":
            self.subset_filenames = self.filenames[self.n_train_images:]
            self.subset_annotations = self.annotations[self.n_train_images:]

            idxs = [i for i, an in enumerate(self.subset_annotations) if an.weather == WeatherCondition.Snowy]
            self.subset_filenames = [fn for i, fn in enumerate(self.subset_filenames) if i in idxs]
            self.subset_annotations = [an for i, an in enumerate(self.subset_annotations) if i in idxs]

            logging.info("Signals in the val (snowy) subset:")

        elif self.subset == "val_daylight":
            self.subset_filenames = self.filenames[self.n_train_images:]
            self.subset_annotations = self.annotations[self.n_train_images:]

            idxs = [i for i, an in enumerate(self.subset_annotations) if an.light == LightCondition.Daylight]
            self.subset_filenames = [fn for i, fn in enumerate(self.subset_filenames) if i in idxs]
            self.subset_annotations = [an for i, an in enumerate(self.subset_annotations) if i in idxs]

            logging.info("Signals in the val (daylight) subset:")
        elif self.subset == "val_twilight":
            self.subset_filenames = self.filenames[self.n_train_images:]
            self.subset_annotations = self.annotations[self.n_train_images:]

            idxs = [i for i, an in enumerate(self.subset_annotations) if an.light == LightCondition.Twilight]
            self.subset_filenames = [fn for i, fn in enumerate(self.subset_filenames) if i in idxs]
            self.subset_annotations = [an for i, an in enumerate(self.subset_annotations) if i in idxs]

            logging.info("Signals in the val (twilight) subset:")
        elif self.subset == "val_dark":
            self.subset_filenames = self.filenames[self.n_train_images:]
            self.subset_annotations = self.annotations[self.n_train_images:]

            idxs = [i for i, an in enumerate(self.subset_annotations) if an.light == LightCondition.Dark]
            self.subset_filenames = [fn for i, fn in enumerate(self.subset_filenames) if i in idxs]
            self.subset_annotations = [an for i, an in enumerate(self.subset_annotations) if i in idxs]

            logging.info("Signals in the val (dark) subset:")
        elif self.subset == "test":
            self.test_idxs = random.choices(np.arange(0, len(self.filenames), 1), k=self.n_test_images)
            self.subset_filenames = [self.filenames[i] for i in self.test_idxs]
            self.subset_annotations = [self.annotations[i] for i in self.test_idxs]
            logging.info("Signals in the test subset:")
        elif self.subset == "daylight":
            self.subset_filenames = [os.path.splitext(an.src_name)[0] for an in self.annotations if
                                     an.light == LightCondition.Daylight]
            self.subset_annotations = [an for an in self.annotations if an.light == LightCondition.Daylight]
            logging.info("Signals in the daylight subset:")
        elif self.subset == "twilight":
            self.subset_filenames = [os.path.splitext(an.src_name)[0] for an in self.annotations if
                                     an.light == LightCondition.Twilight]
            self.subset_annotations = [an for an in self.annotations if an.light == LightCondition.Twilight]
            logging.info("Signals in the twilight subset:")
        elif self.subset == "dark":
            self.subset_filenames = [os.path.splitext(an.src_name)[0] for an in self.annotations if
                                     an.light == LightCondition.Dark]
            self.subset_annotations = [an for an in self.annotations if an.light == LightCondition.Dark]
            logging.info("Signals in the dark subset:")
        elif self.subset == "sunny":
            self.subset_filenames = [os.path.splitext(an.src_name)[0] for an in self.annotations if
                                     an.weather == WeatherCondition.Sunny]
            self.subset_annotations = [an for an in self.annotations if an.weather == WeatherCondition.Sunny]
            logging.info("Signals in the sunny subset:")
        elif self.subset == "cloudy":
            self.subset_filenames = [os.path.splitext(an.src_name)[0] for an in self.annotations if
                                     an.weather == WeatherCondition.Cloudy]
            self.subset_annotations = [an for an in self.annotations if an.weather == WeatherCondition.Cloudy]
            logging.info("Signals in the cloudy subset:")
        elif self.subset == "rainy":
            self.subset_filenames = [os.path.splitext(an.src_name)[0] for an in self.annotations if
                                     an.weather == WeatherCondition.Rainy]
            self.subset_annotations = [an for an in self.annotations if an.weather == WeatherCondition.Rainy]
            logging.info("Signals in the rainy subset:")
        elif self.subset == "foggy":
            self.subset_filenames = [os.path.splitext(an.src_name)[0] for an in self.annotations if
                                     an.weather == WeatherCondition.Foggy]
            self.subset_annotations = [an for an in self.annotations if an.weather == WeatherCondition.Foggy]
            logging.info("Signals in the foggy subset:")
        elif self.subset == "snowy":
            self.subset_filenames = [os.path.splitext(an.src_name)[0] for an in self.annotations if
                                     an.weather == WeatherCondition.Snowy]
            self.subset_annotations = [an for an in self.annotations if an.weather == WeatherCondition.Snowy]
            logging.info("Signals in the snowy subset:")
        elif self.subset == "unknown":
            self.subset_filenames = [os.path.splitext(an.src_name)[0] for an in self.annotations if
                                     an.weather == WeatherCondition.Unknown]
            self.subset_annotations = [an for an in self.annotations if an.weather == WeatherCondition.Unknown]
            logging.info("Signals in the unknown subset:")
        elif self.subset == "all":
            self.subset_filenames = self.filenames
            self.subset_annotations = self.annotations
            logging.info("Signals in the dataset:")
        else:
            raise ValueError("Subset " + self.subset + " is invalid!")

        self.n_targets = 0
        self.signal_distribution = {signal: {"Rel": 0,
                                             "Irrel": 0,
                                             "Total": 0} for signal in GERALDLabels}
        self.weather_distribution = {}
        self.light_distribution = {}

        self.batch_count = 0
        self.im_area = self.model_input_size[0] * self.model_input_size[1]
        logging.info("Image area (Model input): %d px" % self.im_area)

    def __len__(self):
        return len(self.subset_filenames)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        im_path = self.im_path + self.subset_filenames[idx] + ".jpg"

        # Imdecode to support non unicode filepaths
        im = cv2.imdecode(np.fromfile(im_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        an = self.import_single_xml_annotation(self.subset_filenames[idx])

        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB) / 255

        targets = torch.zeros([len(an.objects), 6], dtype=torch.float)

        for i, obj in enumerate(an.objects):
            targets[i, 0] = obj.x_c
            targets[i, 1] = obj.y_c
            targets[i, 2] = obj.w
            targets[i, 3] = obj.h
            targets[i, 4] = obj.label.value
            targets[i, 5] = 0  # Placeholder for sample index

        if self.transform:  # Transforms from Dataset initialization
            im, targets, idx = self.transform((im, targets, idx))

        if self.random_augment:
            if np.random.rand() < 0.25:  # 1/4 chance of image being rotated or flipped
                trfms = [Flip("ud")]
                # trfms = [Rotate(90), Rotate(180), Rotate(270), Flip("ud"), Flip("lr")]
                trfm = np.random.choice(trfms, 1)[0]
                im, targets, idx = trfm((im, targets, idx))
            # if self.model_input_size[0] == self.model_input_size[1] and np.random.rand() < 0.25:  # 1/4 chance of image being rotated (only for quad. input)
            #     trfms = [Rotate(90), Rotate(270)]
            #     trfm = np.random.choice(trfms, 1)[0]
            #     im, targets, idx = trfm((im, targets, idx))
            if np.random.rand() < 0.5:  # 1/2 chance of added color jitter
                trfm = ColorJitter(brightness=(0.75, 1.25), saturation=(0.75, 1.25), hue=.1)
                im, targets, idx = trfm((im, targets, idx))

            if np.random.rand() < 0.1:  # 1/10 chance of added Gaussian Noise
                trfm = GaussianNoise(0.0, .05)
                im, targets, idx = trfm((im, targets, idx))

        return im, targets, idx

    def collate_fn(self, batch):
        trfms = transforms.Compose([ToTensor()])
        for i, sample in enumerate(batch):
            batch[i] = trfms(sample)

        imgs, targets, idxs = list(zip(*batch))

        # Add sample index to targets to relate bounding box to sample image
        for i, boxes in enumerate(targets):
            boxes[:, 5] = i

        imgs = torch.stack(imgs)
        targets = torch.cat(targets, 0)

        self.batch_count += 1
        return imgs, targets, idxs

    def get_all_filenames(self):
        files = sorted(os.listdir(self.an_path))
        filenames = [os.path.splitext(filename)[0] for filename in files]
        return filenames

    def import_xml_annotations(self, filenames):
        logging.info("Importing XML annotations")
        annotations = []

        for filename in tqdm(filenames):
            an = self.import_single_xml_annotation(filename)
            annotations.append(an)

        return annotations

    def import_single_xml_annotation(self, filename, calc_hash=False):
        with open(self.an_path + filename + ".xml", 'rb') as xml_file:
            xml = ET.parse(xml_file)

        root = xml.getroot()

        annotation = Annotation()

        annotation.src_name = root.findall("./filename")[0].text
        annotation.src_width = int(root.findall("./size/width")[0].text)
        annotation.src_height = int(root.findall("./size/height")[0].text)
        annotation.src_depth = int(root.findall("./size/depth")[0].text)
        annotation.src_time = float(annotation.src_name.split("=")[1][:-4]) if "=" in annotation.src_name else 0.0

        if annotation.src_name in self.infos:
            annotation.weather = WeatherCondition[self.infos[annotation.src_name]["weather"]]
            annotation.light = LightCondition[self.infos[annotation.src_name]["light"]]
            annotation.author = self.infos[annotation.src_name]["author"]
            annotation.author_url = self.infos[annotation.src_name]["author url"]
            annotation.src_url = self.infos[annotation.src_name]["source url"]

            phash = self.infos[annotation.src_name]["pHash"]
            annotation.hash = ImageHash(np.array(list(bin(int(phash, 16))[2:])).reshape((8, 8)).astype(np.bool))

        if root.findall("./weather"):
            annotation.weather = WeatherCondition[root.findall("./weather")[0].text]
        if root.findall("./light"):
            annotation.light = LightCondition[root.findall("./light")[0].text]

        objects = root.findall("./object")

        for obj in objects:
            if obj.findall("./bndbox") is not None:
                label = GERALDLabels[obj.findall("./name")[0].text]
                relevant = bool(int(obj.findall("./difficult")[0].text))
                x_min = round(float(obj.findall("./bndbox/xmin")[0].text))
                y_min = round(float(obj.findall("./bndbox/ymin")[0].text))
                x_max = round(float(obj.findall("./bndbox/xmax")[0].text))
                y_max = round(float(obj.findall("./bndbox/ymax")[0].text))
                annotation.add_ground_truth_object(x_min, y_min, x_max, y_max, label, relevant)

        return annotation
