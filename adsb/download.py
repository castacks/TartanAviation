'''
Copyright (c) AirLab Stacks and Carnegie Mellon University.
All rights reserved.

This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
'''

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import ta_download  # noqa: E402

BUCKET = 'tartanaviation-adsb'
SAMPLE = 'kbtp/raw/2022'


def main():
    parser = argparse.ArgumentParser(description='Download TartanAviation ADS-B Dataset')
    ta_download.add_common_args(parser)
    parser.add_argument('--option', type=str, required=True, choices=['Sample', 'Processed', 'Raw', 'All'],
                        help='Sample: one year of raw KBTP data. Processed: filtered trajectories. '
                             'Raw: raw yearly archives. All: Processed + Raw')
    parser.add_argument('--location', type=str, default='Both', choices=['kbtp', 'kagc', 'Both'], help='Data airport location')
    args = parser.parse_args()

    locations = ['kbtp', 'kagc'] if args.location == 'Both' else [args.location]
    objects = ta_download.list_objects(BUCKET)

    paths = []  # bucket keys without the .zip suffix
    if args.option == 'Sample':
        paths.append(SAMPLE)
    for location in locations:
        if args.option in ('Processed', 'All'):
            paths.append(f'{location}/processed')
        if args.option in ('Raw', 'All'):
            paths += sorted(k[:-len('.zip')] for k in objects if k.startswith(f'{location}/raw/') and k.endswith('.zip'))

    # Processed: <save_dir>/<location>/processed/<n>.txt
    # Raw:       <save_dir>/<location>/raw/<year>/<MM-DD-YY>/<n>.csv
    jobs = []
    for path in paths:
        key = f'{path}.zip'
        local_dir = os.path.join(args.save_dir, path)
        flatten = path.endswith('/processed')
        jobs.append(ta_download.Job(key, objects[key], f'{local_dir}.zip', extract_to=local_dir, flatten=flatten))

    ta_download.run(BUCKET, jobs, args.save_dir, args.dry_run)


if __name__ == '__main__':
    main()
