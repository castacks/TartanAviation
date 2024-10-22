# TartanAviation Vision: KAGC

## Overview

This sub-directory contains the scripts to download and process the TartanAviation vision data collected at the KAGC airport. The total size of the downloaded data is 3.3 TB. Post processing, the data size is 22 TB.

For details regarding the dataset, please refer to the [paper](http://arxiv.org/abs/2403.03372).

## Download Instructions
Install MinIO
```sh
pip install minio
```
The `download.py` script can be used to seamlessly download the data. For an overview for the available options, please run:

```sh
python3 download.py --help
```

```output
usage: download.py [-h] [--save_dir SAVE_DIR] --option {Sample,All,Weather_Type,Visibility,Sky_Cover} [--threshold THRESHOLD] [--weather {Snow,Rain,Mist}] [--sky_cover {CLR,BKN,SCT,FEW,OVC}] [--extract_frames] [--visualize_frames]

Download TartanAviation Vision KAGC Dataset

optional arguments:
  -h, --help            show this help message and exit
  --save_dir SAVE_DIR   Directory to save the dataset
  --option {Sample,All,Weather_Type,Visibility,Sky_Cover} Download option based on property
  --threshold THRESHOLD             Visibility Threshold
  --weather {Snow,Rain,Mist}        Weather Type
  --sky_cover {CLR,BKN,SCT,FEW,OVC} Sky Cover Type
  --extract_frames      Extract individual frames from MP4 video
  --visualize_frames    Extract visualized dataset labels as individual frames
```

Please refer to the walkthrough below for more details regarding the download process.

## Sample Download Walkthrough

To download a sample of the data (1.9 GB compressed, 2.1 GB uncompressed), click on this [link](https://airlab-share.andrew.cmu.edu:8081/tartanaviation/vision/kagc_final/1_2023-02-22-15-21-49.zip).

To download using the script, run the following command:

```sh
python3 download.py --option Sample
```

The script will download the data by default to the `./data` directory. The example directory structure will be as follows:

```
./data
└── 1_2023-02-22-15-21-49
    ├── 1_2023-02-22-15-21-49_sink
    │   ├── ...
    ├── 1_2023-02-22-15-21-49.mp4
    ├── 1_2023-02-22-15-21-49_labels.zip
    ├── 1_2023-02-22-15-21-49_acft_sink.pkl
    ├── 1_2023-02-22-15-21-49_sink_adsb.pkl
    ├── 1_2023-02-22-15-21-49_sink_verified.avi
    ├── 1_2023-02-22-15-21-49_subtitle.srt
```

## Extracting Individual Frames

To further process the data and extract individual frames from the MP4 videos, please run the following command:

```
python3 download.py --option Sample --extract_frames
```

Please note that extracting frames from the downloaded videos requires [FFMPEG](https://ffmpeg.org/). Furthermore, it is a time consuming process.

We also provide an example [PyTorch](https://pytorch.org/get-started/locally/) dataloader to load the extracted frames and labels in the `dataloader.py` script.

## Citation

Please cite the following paper if you find this dataset helpful in your work:

```
@article{patrikar2024tartanaviation,
	title={TartanAviation: Image, Speech, and ADS-B Trajectory Datasets for Terminal Airspace Operations}, 
	author={Jay Patrikar and Joao Dantas and Brady Moon and Milad Hamidi and Sourish Ghosh and Nikhil Keetha and Ian Higgins and Atharva Chandak and Takashi Yoneyama and Sebastian Scherer},
	year={2024},
	eprint={2403.03372},
	archivePrefix={arXiv},
	primaryClass={cs.LG},
	url={https://arxiv.org/pdf/2403.03372.pdf}
}
```