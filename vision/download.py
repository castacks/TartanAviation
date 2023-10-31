'''
Copyright (c) AirLab Stacks and Carnegie Mellon University.
All rights reserved.

Author: Nikhil Varma Keetha

This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
'''

import argparse
import csv
import os


parser = argparse.ArgumentParser(description='Download TartanAviation Vision KAGC Dataset')
parser.add_argument('--save_dir', type=str, default='./data', help='Directory to save the dataset')
parser.add_argument('--option', type=str, required=True, choices=['Sample', 'All', 'Weather_Type', 'Visibility', 'Sky_Cover'], help='Download option based on property')
parser.add_argument('--threshold', type=float, default=5, help='Visibility Threshold')
parser.add_argument('--weather', type=str, default='Snow', choices=['Snow', 'Rain', 'Mist'], help='Weather Type')
parser.add_argument('--sky_cover', type=str, default='CLR', choices=['CLR', 'BKN', 'SCT', 'FEW', 'OVC'], help='Sky Cover Type')
parser.add_argument('--extract_frames', action='store_true', help='Extract individual frames from MP4 video')
parser.add_argument('--visualize_frames', action='store_true', help='Extract visualized dataset labels as individual frames')
args = parser.parse_args()

# Print the selected option
print(f'Selected Option: {args.option}')
# Print the selected values for weather type, visibility threshold and sky cover
if args.option == 'Weather_Type':
    print(f'Selected Weather Type: {args.weather}')
elif args.option == 'Visibility':
    print(f'Selected Visibility Threshold: {args.threshold}')
elif args.option == 'Sky_Cover':
    print(f'Selected Sky Cover: {args.sky_cover}')

# Read weather_stats.csv file
with open('./weather_stats.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    video_folders = []
    for row in reader:
        video_name, aircraft, visibility, mist, fog, haze, sky_cover_l1, cloud_height_l1, rain, snow = row
        # Download single sample folder
        if args.option == 'Sample':
            sample_video_name = '1_2023-02-22-15-21-49'
            video_folders.append(sample_video_name)
            break
        # Download all video folders
        elif args.option == 'All':
            video_folders.append(video_name)
        # Download video folders based on weather type
        elif args.option == 'Weather_Type':
            if args.weather == 'Snow' and snow == "TRUE":
                video_folders.append(video_name)
            elif args.weather == 'Rain' and rain == "TRUE":
                video_folders.append(video_name)
            elif args.weather == 'Mist' and mist == "TRUE":
                video_folders.append(video_name)
        # Download video folders based on visibility threshold
        elif args.option == 'Visibility' and float(visibility) <= args.threshold:
            video_folders.append(video_name)
        # Download video folders based on sky cover
        elif args.option == 'Sky_Cover' and sky_cover_l1 == args.sky_cover:
            video_folders.append(video_name)

# Print number of video folders
print(f'Number of Video Folders: {len(video_folders)}')

# Create Save Directory
if not os.path.exists(args.save_dir):
    os.makedirs(args.save_dir, exist_ok=True)

# Define Base URL for download
base_url = "http://airlab-share.andrew.cmu.edu/tartanaviation/vision/kagc_final"

# Download video folders using wget
for folder in video_folders:
    # Check if folder already exists
    if not os.path.exists(os.path.join(args.save_dir, folder)):
        download_file = f'{base_url}/{folder}.zip'
        
        # Remove zip file if it already exists
        if not os.path.exists(os.path.join(args.save_dir, f'{folder}.zip')):
            os.system(f'rm {os.path.join(args.save_dir, f"{folder}.zip")}')
        
        # Download zip file to save directory
        ret = os.system(f'wget -P {args.save_dir} {download_file}')

        # Unzip the downloaded file
        if ret == 0:
            ret = os.system(f'unzip {os.path.join(args.save_dir, folder)}.zip -d {args.save_dir}')
            # Remove the zip file
            if ret == 0:
                os.system(f'rm {os.path.join(args.save_dir, folder)}.zip*')
                # Unzip the labels zip file
                os.system(f'unzip {os.path.join(args.save_dir, folder, f"{folder}_labels.zip")} -d {os.path.join(args.save_dir, folder)}')
            else:
                print(f'Please download Unzip')
                break
        # Exit if download fails
        elif ret != 0:
            print(f'Failed to download {folder}')
            break
    # Skip download if folder already exists
    else:
        print(f'{folder} already exists in {args.save_dir}')
    
    # Check if sink folder already exists
    if args.extract_frames:
        # Convert MP4 video to PNG frames if no png frames exist
        sample_frame_name = os.path.join(args.save_dir, folder, f'{folder}_sink', '2.png')
        if not os.path.exists(sample_frame_name):
            video_path = os.path.join(args.save_dir, folder, f'{folder}.mp4')
            frame_save_dir = os.path.join(args.save_dir, folder, f'{folder}_sink')
            os.makedirs(frame_save_dir, exist_ok=True)
            ret = os.system(f'ffmpeg -i {video_path} -vf "fps=24" -start_number 2 {os.path.join(frame_save_dir, "%d.png")}')
            if ret != 0:
                break

    # Check if visualization folder already exists
    if not os.path.exists(os.path.join(args.save_dir, folder, f'{folder}_sink_verified')):
        # Convert Visualized Videos to PNG frames
        if args.visualize_frames:
            video_path = os.path.join(args.save_dir, folder, f'{folder}_sink_verified.avi')
            frame_save_dir = os.path.join(args.save_dir, folder, f'{folder}_vis_sink')
            os.makedirs(frame_save_dir, exist_ok=True)
            ret = os.system(f'ffmpeg -i {video_path} -vf "fps=24" -start_number 2 {os.path.join(frame_save_dir, "%d.png")}')
            if ret != 0:
                break