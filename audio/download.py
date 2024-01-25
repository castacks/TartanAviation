'''
Copyright (c) AirLab Stacks and Carnegie Mellon University.
All rights reserved.

Authors: Brady Moon, Nikhil Varma Keetha

This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
'''

import argparse
import os
import requests

def download_file(base_url, save_dir, audio_path):
    # get the file name of audio_path
    audio_name = os.path.basename(audio_path)
    audio_save_path = os.path.join(args.save_dir, audio_path)
    # Check if folder already exists
    if not os.path.exists(audio_save_path):
        download_file = f'{base_url}/{audio_path}.zip'
        
        # Check if file exists
        response = requests.head(download_file, allow_redirects=True)

        if response.status_code == 200:
            # Make directory
            os.makedirs(audio_save_path, exist_ok=True)

            # Download zip file to save directory
            ret = os.system(f'wget -P {save_dir} {download_file}')

            # Unzip the downloaded file
            if ret == 0:
                ret = os.system(f'unzip -j {os.path.join(save_dir, audio_name)}.zip -d {audio_save_path}')
                # Remove the zip file
                if ret == 0:
                    os.system(f'rm {os.path.join(save_dir, audio_name)}.zip*')
                else:
                    print(f'Please download Unzip (sudo apt install unzip)')
            # Exit if download fails
            elif ret != 0:
                print(f'Failed to download {audio_path}')
        # else:
        #     print(f'File {download_file} does not exist on the server.')

    # Skip download if folder already exists
    else:
        print(f'{audio_path} already exists in {save_dir}')
    # download audio

parser = argparse.ArgumentParser(description='Download TartanAviation Audio Dataset')
parser.add_argument('--save_dir', type=str, default='./data', help='Directory to save the dataset')
parser.add_argument('--option', type=str, required=True, choices=['Sample', 'All', 'Date_Range', 'Raw'], help='Download option based on property')
parser.add_argument('--location', type=str, default='Both', choices=['kbtp', 'kagc', 'Both'], help='Data airport location')
parser.add_argument('--start_date', type=str, default='2020-09', help='Start Date (YYYY-MM)')
parser.add_argument('--end_date', type=str, default='2023-02', help='End Date (YYYY-MM)')
args = parser.parse_args()

# Print the selected option
print(f'Selected Option: {args.option}')
print(f'Selected Location: {args.location}')
# Print the selected values for weather type, visibility threshold and sky cover
if args.option == 'Date_Range':
    print(f'Selected Start Date: {args.start_date}')
    print(f'Selected End Date: {args.end_date}')

# Create Save Directory
if not os.path.exists(args.save_dir):
    os.makedirs(args.save_dir, exist_ok=True)


# Define Base URL for download
base_url = "http://airlab-share.andrew.cmu.edu/tartanaviation/audio"

if args.option == 'Date_Range' or args.option == 'All':
    start_date = '2020-09'
    end_date = '2023-02'
    if args.option == 'Date_Range':
        start_date = args.start_date
        end_date = args.end_date
    # Go through each location
    if args.location == 'Both':
        locations = ['kbtp', 'kagc']
    else:
        locations = [args.location]

    for location in locations:
        # Go through each date in range
        for year in range(int(start_date.split('-')[0]), int(end_date.split('-')[0])+1):
            start_month = int(start_date.split('-')[1]) if year == int(start_date.split('-')[0]) else 1
            end_month = int(end_date.split('-')[1]) if year == int(end_date.split('-')[0]) else 12
            for month in range(start_month, end_month+1):
                for day in range(1, 32):
                    audio_path = f'{location}/{year}/{month:02d}/{month:02d}-{day:02d}-{str(year)[-2:]}_audio'
                    download_file(base_url, args.save_dir, audio_path)
elif args.option == 'Sample':
    sample_audio_path = 'kbtp/2020/11/11-02-20_audio'
    download_file(base_url, args.save_dir, sample_audio_path)
elif args.option == 'Raw':
    audio_path = 'tartanaviation_raw_audio/'

    audio_save_path = os.path.join(args.save_dir, audio_path)
    # Check if folder already exists
    download_files = f'{base_url}/{audio_path}'

    # Download zip file to save directory
    ret = os.system(f'wget -r -np -R index.html -P {args.save_dir} {download_files}')

    # Unzip the downloaded file
    if ret == 0:
        print(f'Download {audio_path}')
    # Exit if download fails
    elif ret != 0:
        print(f'Failed to download {audio_path}')
else:
    print('Invalid option')

