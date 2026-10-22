'''
Copyright (c) AirLab Stacks and Carnegie Mellon University.
All rights reserved.

Author: Nikhil Varma Keetha, Brady Moon

This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
'''

import argparse
import csv
import os
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import ta_download  # noqa: E402

BUCKET = 'tartanaviation-vision'
SAMPLE = '1_2023-02-22-15-21-49'


def select_videos(args):
    '''Pick video names from weather_stats.csv according to --option.'''
    if args.option == 'Sample':
        return [SAMPLE]
    with open(os.path.join(HERE, 'weather_stats.csv'), newline='') as f:
        rows = list(csv.DictReader(f))
    if args.option == 'All':
        keep = rows
    elif args.option == 'Weather_Type':
        keep = [r for r in rows if r[args.weather.lower()] == 'TRUE']
    elif args.option == 'Visibility':
        keep = [r for r in rows if float(r['visibility']) <= args.threshold]
    else:  # Sky_Cover
        keep = [r for r in rows if r['sky_cover_l1'] == args.sky_cover]
    return [r['video_name'] for r in keep]


def extract_frames(video_path, frame_dir):
    '''Split a video into <frame_dir>/<n>.png at 24 fps, numbered from 2 to match the labels.'''
    marker = os.path.join(frame_dir, '.frames_complete')  # absent if a previous run was interrupted
    if os.path.exists(marker):
        return True
    os.makedirs(frame_dir, exist_ok=True)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-stats', '-i', video_path, '-vf', 'fps=24', '-start_number', '2',
           os.path.join(frame_dir, '%d.png')]
    if subprocess.run(cmd).returncode != 0:
        print(f'  Failed to extract frames from {video_path}')
        return False
    open(marker, 'w').close()
    return True


def main():
    parser = argparse.ArgumentParser(description='Download TartanAviation Vision KAGC Dataset')
    ta_download.add_common_args(parser)
    parser.add_argument('--option', type=str, required=True, choices=['Sample', 'All', 'Weather_Type', 'Visibility', 'Sky_Cover'],
                        help='Download option based on property')
    parser.add_argument('--threshold', type=float, default=5, help='Visibility threshold in statute miles (with --option Visibility)')
    parser.add_argument('--weather', type=str, default='Snow', choices=['Snow', 'Rain', 'Mist'], help='Weather type (with --option Weather_Type)')
    parser.add_argument('--sky_cover', type=str, default='CLR', choices=['CLR', 'BKN', 'SCT', 'FEW', 'OVC'], help='Sky cover (with --option Sky_Cover)')
    parser.add_argument('--extract_frames', action='store_true', help='Extract individual frames from MP4 video')
    parser.add_argument('--visualize_frames', action='store_true', help='Extract visualized dataset labels as individual frames')
    args = parser.parse_args()

    if (args.extract_frames or args.visualize_frames) and not args.dry_run and shutil.which('ffmpeg') is None:
        sys.exit('--extract_frames / --visualize_frames need ffmpeg on your PATH (https://ffmpeg.org/).')

    videos = select_videos(args)
    print(f'Selected {len(videos)} video(s).')
    objects = ta_download.list_objects(BUCKET)

    # Each video is extracted into <save_dir>/<video>/
    jobs = []
    for name in videos:
        local = os.path.join(args.save_dir, name)
        jobs.append(ta_download.Job(f'{name}.zip', objects[f'{name}.zip'], f'{local}.zip', extract_to=local, flatten=True))
    for job in ta_download.run(BUCKET, jobs, args.save_dir, args.dry_run):
        labels = os.path.join(job.extract_to, f'{os.path.basename(job.extract_to)}_labels.zip')
        if os.path.exists(labels):
            with zipfile.ZipFile(labels) as zf:
                zf.extractall(job.extract_to)
    if args.dry_run:
        return

    for name in videos:
        folder = os.path.join(args.save_dir, name)
        if not os.path.isdir(folder):
            continue
        if args.extract_frames:
            print(f'Extracting frames: {name}')
            extract_frames(os.path.join(folder, f'{name}.mp4'), os.path.join(folder, f'{name}_sink'))
        if args.visualize_frames:
            print(f'Extracting label visualization frames: {name}')
            extract_frames(os.path.join(folder, f'{name}_sink_verified.avi'), os.path.join(folder, f'{name}_vis_sink'))


if __name__ == '__main__':
    main()
