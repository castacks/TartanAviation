# TartanAviation: ADS-B Data

## Overview

This directory contains the scripts to download the TartanAviation ADS-B data. The total size of the downloaded data is 12 GBs uncompressed and 1.9 GBs compressed. This directory also contains the scripts that were used to filter and analyze the trajectory data.

For details regarding the dataset, please refer to the [paper](http://arxiv.org/abs/2403.03372).

## Download Instructions
Install MinIO
```sh
pip install minio requests
```

The `download.py` script can be used to seamlessly download the data. For an overview for the available options, please run:

```sh
python3 download.py --help
```

```output
usage: download.py [-h] [--save_dir SAVE_DIR] --option {Sample,All,Processed,Raw} [--location {kbtp,kagc,Both}]

Download TartanAviation ADS-B Dataset

options:
  -h, --help            show this help message and exit
  --save_dir SAVE_DIR   Directory to save the dataset
  --option {Sample,All,Processed,Raw}  Download option based on property
  --location {kbtp,kagc,Both}   Data airport location
```

Please refer to the walkthrough below for more details regarding the download process.

## Sample Download Walkthrough

To download a sample of the data (733 Mb compressed, 3.4 GB uncompressed), click on this [link](http://airlab-share.andrew.cmu.edu/tartanaviation/trajectory/kbtp/raw/2022.zip):

To download using the script, run the following command:

```
python3 download.py --option Sample
```

The script will download the data by default to the `./data` directory. The example directory structure will be as follows:

```
./data
└── kbtp
    └── raw  
        └── 2022
            └── 11-02-20
                    ├── 1.csv
```

## Raw data

The raw data can be downloaded by running the following command:

```sh
python3 download.py --option Raw
```

The scripts `process.py`  can be used to filter and process the raw data after being uncompressed. 

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
