'''
Copyright (c) AirLab Stacks and Carnegie Mellon University.
All rights reserved.

This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
'''

import argparse
import os
import requests
import boto3
from botocore import UNSIGNED
from botocore.config import Config
from botocore.exceptions import ClientError

def download_file(base_url, save_dir, adsb_path, unzip=False):
    # get the file name of adsb_path
    adsb_name = os.path.basename(adsb_path)
    adsb_save_path = os.path.join(args.save_dir, adsb_path)
    # Check if folder already exists
    if not os.path.exists(adsb_save_path):
        download_file = f'{base_url}/{adsb_path}.zip'
        # Check if file exists
        response = requests.head(download_file, allow_redirects=True)

        if response.status_code == 200:
            # Make directory
            os.makedirs(adsb_save_path, exist_ok=True)
            print(adsb_save_path,save_dir)
            # Download zip file to save directory
            ret = os.system(f'wget -P {save_dir} {download_file}')

            # Unzip the downloaded file
            if ret == 0 and unzip == True:
                ret = os.system(f'unzip {os.path.join(save_dir, adsb_name)}.zip -d {adsb_save_path}')
                # Remove the zip file
                if ret == 0:
                    os.system(f'rm {os.path.join(save_dir, adsb_name)}.zip*')
                else:
                    print(f'Please download Unzip (sudo apt install unzip)')
            elif ret==0 and unzip == False:
                print("Not Unzipping")
            # Exit if download fails
            elif ret != 0:
                print(f'Failed to download {adsb_path}')
        # else:
        #     print(f'File {download_file} does not exist on the server.')

    # Skip download if folder already exists
    else:
        print(f'{adsb_path} already exists in {save_dir}')
    # download adsb

def download_file_from_bucket(client, bucket_name, save_dir, adsb_path,unzip=False):
    # get the file name of adsb_path
    adsb_name = os.path.basename(adsb_path)
    adsb_save_path = os.path.join(args.save_dir, adsb_path)
    # Check if folder already exists
    if not os.path.exists(adsb_save_path):
        download_file = f'{adsb_path}.zip'
        download_dest = f'{adsb_save_path}/{adsb_name}.zip'

        # Check if file exists
        try:
            client.head_object(Bucket=bucket_name, Key=download_file)
        except ClientError as err:
            code = err.response.get("Error", {}).get("Code", "")
            # Common "not found" codes across S3-compatible backends
            if code in ("404", "NoSuchKey", "NotFound"):
                return  # object does not exist
            else:
                print(f"Failed to lookup {adsb_path or download_file}")
                print(f"An error occurred: {err}")
                return
        
        # Make directory
        os.makedirs(adsb_save_path, exist_ok=True)

        # Download zip file to save directory
        try:
            print("\n","Downloading ",download_file," to ",download_dest)
            response = client.get_object(Bucket=bucket_name, Key=download_file)
            with open(download_dest, 'wb') as f:
                for chunk in response['Body'].iter_chunks(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
        except ClientError as err:
            # Exit if download fails
            print(f'Failed to download {adsb_path}')
            print(f"An error occurred: {err}")
            return

        if unzip:
            # Unzip the downloaded file
            ret = os.system(f'unzip -j {os.path.join(save_dir, adsb_name)}.zip -d {adsb_save_path}')
            # Remove the zip file
            if ret == 0:
                os.system(f'rm {os.path.join(save_dir, adsb_name)}.zip*')
            else:
                print(f'Please download Unzip (sudo apt install unzip)')

    # Skip download if folder already exists
    else:
        print(f'{adsb_path} already exists in {save_dir}')

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
endpoint_url = "https://airlab-cloud.andrew.cmu.edu:8080/swift/v1/AUTH_ac8533a83cff4d48bc8c608ad222d330"  
bucket_name = "tartanaviation-adsb"

client = boto3.client("s3", endpoint_url=endpoint_url, config=Config(signature_version=UNSIGNED))

# Go through each location
if args.location == 'Both':
    locations = ['kbtp', 'kagc']
else:
    locations = [args.location]
if args.option == 'All':



    for location in locations:
        file_path = f'{location}/processed'
        download_file_from_bucket(client, bucket_name, args.save_dir, file_path)
        file_path = f'{location}/raw/2021'
        download_file_from_bucket(client, bucket_name, args.save_dir, file_path, unzip=False)
        file_path = f'{location}/raw/2022'
        download_file_from_bucket(client, bucket_name, args.save_dir, file_path, unzip=False)
        if location == 'kbtp':
            file_path = f'{location}/raw/2020'
            download_file_from_bucket(client, bucket_name, args.save_dir, file_path, unzip=False)

        
elif args.option == 'Sample':
    sample_path = 'kbtp/raw/2022'
    download_file_from_bucket(client, bucket_name, args.save_dir, sample_path, unzip=False)

elif args.option == 'Raw':
    for location in locations:
        file_path = f'{location}/raw/2021'
        download_file_from_bucket(client, bucket_name, args.save_dir, file_path, unzip=False)
        file_path = f'{location}/raw/2022'
        download_file_from_bucket(client, bucket_name, args.save_dir, file_path, unzip=False)
        if location == 'kbtp':
            file_path = f'{location}/raw/2020'
            download_file_from_bucket(client, bucket_name, args.save_dir, file_path, unzip=False)

elif args.option == 'Processed':
    for location in locations:
        file_path = f'{location}/processed'
        download_file_from_bucket(client, bucket_name, args.save_dir, file_path)
else:
    print("No Valid Option")
