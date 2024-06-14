# TartanAviation: Speech

## Overview

This directory contains the scripts to download the TartanAviation speech data. The total size of the downloaded data is 2.15 TBs uncompressed and 505.2 GBs compressed. This directory also contains the scripts that were used to filter and analyze the speech data.

For details regarding the dataset, please refer to the [paper](http://arxiv.org/abs/2403.03372).

## Download Instructions
The `download.py` script can be used to seamlessly download the data. For an overview for the available options, please run:

```
python3 download.py --help
```

```output
usage: download.py [-h] [--save_dir SAVE_DIR] --option {Sample,All,Date_Range} [--location {kbtp,kagc,Both}]
                   [--start_date START_DATE] [--end_date END_DATE]

Download TartanAviation Audio Dataset

options:
  -h, --help            show this help message and exit
  --save_dir SAVE_DIR   Directory to save the dataset
  --option {Sample,All,Date_Range,Raw}  Download option based on property
  --location {kbtp,kagc,Both}   Data airport location
  --start_date START_DATE       Start Date (YYYY-MM)
  --end_date END_DATE           End Date (YYYY-MM)
```

Please refer to the walkthrough below for more details regarding the download process.

## Sample Download Walkthrough

To download a sample of the data (314 MB compressed, 1.2 GB uncompressed), run the following command:

```
python3 download.py --option Sample
```

The sample contains 13 audio files and their corresponding metadata. The audio files are in the `.wav` format and the metadata are in the `.txt` format.

The script will download the data by default to the `./data` directory. The example directory structure will be as follows:

```
./data
└── kbtp
    └── 2020
        └── 11
            └── 11-02-20_audio
                ├── 1.txt
                ├── 1.wav
                ├── 2.txt
                ├── 2.wav
                ├── ...
                ├── 15.txt
                ├── 15.wav
```

## Raw data

The raw data can be downloaded by running the following command:

```
python3 download.py --option Raw
```
This will download the 630 GB compressed files.

The scripts `filter.sh` and `analyze.sh` can be used to filter and analyze the raw data after being uncompressed. The output of the `analyze.sh` script can be seen in the file `analyze_output.txt`.


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