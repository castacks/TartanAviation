'''
Copyright (c) AirLab Stacks and Carnegie Mellon University.
All rights reserved.

This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
'''

import argparse
import os
import requests

def download_file(base_url, save_dir, audio_path, unzip=True):
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
            print(audio_save_path,save_dir)
            # Download zip file to save directory
            ret = os.system(f'wget -P {save_dir} {download_file}')

            # Unzip the downloaded file
            if ret == 0 and unzip == True:
                ret = os.system(f'unzip {os.path.join(save_dir, audio_name)}.zip -d {audio_save_path}')
                # Remove the zip file
                if ret == 0:
                    os.system(f'rm {os.path.join(save_dir, audio_name)}.zip*')
                else:
                    print(f'Please download Unzip (sudo apt install unzip)')
            elif ret==0 and unzip == False:
                print("Not Unzipping")
            # Exit if download fails
            elif ret != 0:
                print(f'Failed to download {audio_path}')
        # else:
        #     print(f'File {download_file} does not exist on the server.')

    # Skip download if folder already exists
    else:
        print(f'{audio_path} already exists in {save_dir}')
    # download audio

parser = argparse.ArgumentParser(description='Download TartanAviation ADS-B Dataset')
parser.add_argument('--save_dir', type=str, default='./data', help='Directory to save the dataset')
parser.add_argument('--option', type=str, required=True, choices=['Sample', 'Processed', 'All', 'Raw'], help='Download option based on property')
parser.add_argument('--location', type=str, default='Both', choices=['kbtp', 'kagc', 'Both'], help='Data airport location')
args = parser.parse_args()

# Print the selected option
print(f'Selected Option: {args.option}')

# Create Save Directory
if not os.path.exists(args.save_dir):
    os.makedirs(args.save_dir, exist_ok=True)


# Define Base URL for download
base_url = "http://airlab-share.andrew.cmu.edu/tartanaviation/trajectory"
# Go through each location
if args.location == 'Both':
    locations = ['kbtp', 'kagc']
else:
    locations = [args.location]
if args.option == 'All':



    for location in locations:
        file_path = f'{location}/processed'
        download_file(base_url, args.save_dir, file_path)
        file_path = f'{location}/raw/2021'
        download_file(base_url, args.save_dir, file_path, unzip=True)
        file_path = f'{location}/raw/2022'
        download_file(base_url, args.save_dir, file_path, unzip=True)
        if location == 'kbtp':
            file_path = f'{location}/raw/2020'
            download_file(base_url, args.save_dir, file_path, unzip=True)

        
elif args.option == 'Sample':
    sample_audio_path = 'kbtp/raw/2022'
    download_file(base_url, args.save_dir, sample_audio_path)

elif args.option == 'Raw':
    for location in locations:
        file_path = f'{location}/raw/2021'
        download_file(base_url, args.save_dir, file_path, unzip=True)
        file_path = f'{location}/raw/2022'
        download_file(base_url, args.save_dir, file_path, unzip=True)
        if location == 'kbtp':
            file_path = f'{location}/raw/2020'
            download_file(base_url, args.save_dir, file_path, unzip=True)

elif args.option == 'Processed':
    for location in locations:
        file_path = f'{location}/processed'
        download_file(base_url, args.save_dir, file_path)
else:
    print("No Valid Option")