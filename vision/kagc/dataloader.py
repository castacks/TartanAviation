'''
Copyright (c) AirLab Stacks and Carnegie Mellon University.
All rights reserved.

Authors: Dina Long, Nikhil Varma Keetha

This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
'''

import csv
from natsort import natsorted
import os
import shlex
from typing import Optional

import cv2
import numpy as np
import torch
from torch.utils import data


class KAGC(data.Dataset):
    r"""A torch Dataset for loading images and groundtruth labels. Will fetch sequences of grayscale images, bbox labels, and video name.
    Expects the following folder structure for the KAGC dataset:
    .. code-block::
        Root Directory/
        ├─ 0_2022-11-17-12-05-08/
        │  ├─ 0_2022-11-17-12-05-08_sink/
        │  │  ├─ 2.png
        │  │  ├─ 3.png
        |  |  |  .
        |  |  |  .
        │  │  ├─ 3939.label
        │  │  ├─ 3940.label
        |  |  .
        |  |  .
        ├─ 0_2022-11-17-12-16-10/
        │  ├─ 0_2022-11-17-12-16-10_sink/
        │  │  ├─ 2.png
        │  │  ├─ 3.png
        |  |  |  .
        |  |  |  .


    Example of sequence creation from frames with `seqlen=4`, `dilation=1`, `stride=3`, and `start=2`:
    .. code-block::
                                            sequence0
                        ┎───────────────┲───────────────┲───────────────┒
                        |               |               |               |
        frame0  frame1  frame2  frame3  frame4  frame5  frame6  frame7  frame8  frame9  frame10  frame11 ...
                                                |               |               |                |
                                                └───────────────┵───────────────┵────────────────┚
                                                                    sequence1
    Args:
        basedir (str): Path to the base directory containing the images.
        seqlen (int): Number of frames to use for each sequence of frames. Default: 2
        dilation (int or None): Number of (original video's) frames to skip between two consecutive
            frames in the extracted sequence. See above example if unsure.
            If None, will set `dilation = 0`. Default: None
        stride (int or None): Number of frames between the first frames of two consecutive extracted sequences.
            See above example if unsure. If None, will set `stride = seqlen * (dilation + 1)`
            (non-overlapping sequences). Default: 1
        start (int or None): Index of the frame from which to start extracting sequences for every video.
            If None, will start from the first frame. Default: None
        end (int): Index of the frame at which to stop extracting sequences for every video.
            If None, will continue extracting frames until the end of the video. Default: None
        height (int): Spatial height to resize frames to. Default: 2048
        width (int): Spatial width to resize frames to. Default: 2448
    """

    def __init__(
        self,
        basedir: str,
        height: int = 2048,
        width: int = 2448,
        gt_height: int = None,
        gt_width: int = None,
        seqlen: int = 2,
        stride: Optional[int] = 1,
        dilation: Optional[int] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
        seq_names_file: str = "",
    ):
        super(KAGC, self).__init__()

        self.basedir = os.path.normpath(basedir)
        if not os.path.isdir(self.basedir):
            raise ValueError("Base Directory: {} doesn't exist".format(basedir))

        self.height = height
        self.width = width

        if not isinstance(gt_height, int):
            raise TypeError(
                "Ground Truth height must be int. Got {0}.".format(type(gt_height))
            )
        if not isinstance(gt_width, int):
            raise TypeError(
                "Ground Truth width must be int. Got {0}.".format(type(gt_width))
            )

        self.gt_height = gt_height
        self.gt_width = gt_width

        if not isinstance(seqlen, int):
            raise TypeError("seqlen must be int. Got {0}.".format(type(seqlen)))
        if not (isinstance(stride, int) or stride is None):
            raise TypeError("stride must be int or None. Got {0}.".format(type(stride)))
        if not (isinstance(dilation, int) or dilation is None):
            raise TypeError(
                "dilation must be int or None. Got {0}.".format(type(dilation))
            )
        dilation = dilation if dilation is not None else 0
        stride = stride if stride is not None else seqlen * (dilation + 1)
        self.seqlen = seqlen
        self.stride = stride
        self.dilation = dilation
        if seqlen < 0:
            raise ValueError("seqlen must be positive. Got {0}.".format(seqlen))
        if dilation < 0:
            raise ValueError('"dilation" must be positive. Got {0}.'.format(dilation))
        if stride < 0:
            raise ValueError("stride must be positive. Got {0}.".format(stride))

        if not (isinstance(start, int) or start is None):
            raise TypeError("start must be int or None. Got {0}.".format(type(start)))
        if not (isinstance(end, int) or end is None):
            raise TypeError("end must be int or None. Got {0}.".format(type(end)))
        start = start if start is not None else 0
        self.start = start
        self.end = end
        if start < 0:
            raise ValueError("start must be positive. Got {0}.".format(stride))
        if not (end is None or end > start):
            raise ValueError(
                "end ({0}) must be None or greater than start ({1})".format(end, start)
            )

        self.video_name_data = []
        self.img_data = []
        self.label_data = []

        seq_names = []
        if os.path.exists(seq_names_file):
            with open(seq_names_file, mode="r") as file:
                csvFile = csv.reader(file, delimiter=",")

                for lines in csvFile:
                    seq_names.extend(lines)
        else:
            raise ValueError(
                "video names file {0} doesn't exist.".format(seq_names_file)
            )

        for seq_name in seq_names:
            if os.path.exists(os.path.join(basedir, seq_name)):
                video_name = seq_name
                img_dir = os.path.join(basedir, video_name, video_name + "_sink")

                img_list = [
                    os.path.join(img_dir, x)
                    for x in natsorted(os.listdir(img_dir))
                    if x.endswith(".png")
                ]
                label_list = [os.path.splitext(x)[0] + ".label" for x in img_list]

                idx = np.arange(self.seqlen) * (self.dilation + 1)
                video_len = len(img_list)
                if end is not None:
                    video_len = end
                for start_index in range(self.start, video_len, self.stride):
                    if start_index + idx[-1] >= video_len:
                        break
                    inds = start_index + idx
                    self.img_data.append([img_list[ind] for ind in inds])
                    self.label_data.append([label_list[ind] for ind in inds])
                    self.video_name_data.append(video_name)
            else:
                print("Video " + seq_name + " doesn't exist.")

        self.num_sequences = len(self.img_data)

    def __len__(self):
        r"""Returns the length of the dataset."""
        return self.num_sequences

    def __getitem__(self, idx: int):
        r"""Returns the data from the sequence at index idx.
        Returns:
            img_seq (torch.Tensor): Sequence of grayscale images of each frame
            label_seq (List): Sequence of ground truth labels for each frame
            video_name (str): Video Name
        Shape:
            - img_seq: :math:`(L, H, W)` where `L` denotes sequence length
            - label_seq: List of length `L`
        """

        img_seq_path = self.img_data[idx]
        label_seq_path = self.label_data[idx]
        video_name = self.video_name_data[idx]

        img_seq = []
        label_seq = [[], [], [], [], [], []]

        for i in range(self.seqlen):
            image = cv2.imread(img_seq_path[i], 0)

            if image is None:
                return self.__getitem__(idx + 1)

            if (image.shape[0] != self.height) or (image.shape[1] != self.width):
                image = cv2.resize(
                    image, (self.width, self.height), interpolation=cv2.INTER_LINEAR
                )

            image = torch.from_numpy(image).float()
            image /= 255
            img_seq.append(image)

            gt_boxes = []
            flight_ids = []
            distances = []
            manufacturers = []
            model_names = []
            obj_types = []
            if os.path.exists(label_seq_path[i]):
                with open(label_seq_path[i], "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        parts = shlex.split(line.strip("\n"))

                        if len(parts) != 9:
                            return self.__getitem__(idx + 1)

                        gt_boxes.append(
                            [
                                int(float(parts[0]) / self.gt_width * self.width),
                                int(float(parts[1]) / self.gt_height * self.height),
                                int(float(parts[2]) / self.gt_width * self.width),
                                int(float(parts[3]) / self.gt_height * self.height),
                            ]
                        )
                        flight_ids.append(int(parts[4]))
                        distances.append(float(parts[5]))
                        manufacturers.append(parts[6])
                        model_names.append(parts[7])
                        obj_types.append(parts[8])

            label_seq[0].append(gt_boxes)
            label_seq[1].append(flight_ids)
            label_seq[2].append(distances)
            label_seq[3].append(manufacturers)
            label_seq[4].append(model_names)
            label_seq[5].append(obj_types)

        img_seq = torch.stack(img_seq, 0)

        return img_seq, label_seq, video_name, img_seq_path

    def custom_collate(self, batch):
        r"""Puts each tensor data field into a tensor with outer dimension batch size
        and Puts list data into list with length batch size"""

        tensors = []
        list_1 = []
        list_2 = []
        list_3 = []

        for i in range(len(batch)):
            tensors.append(batch[i][0])
            list_1.extend(batch[i][1])
            list_2.append(batch[i][2])
            list_3.append(batch[i][3])

        tensor = torch.stack(tensors, 0)

        return tensor, list_1, list_2, list_3