'''
Copyright (c) AirLab Stacks and Carnegie Mellon University.
All rights reserved.

Authors: Brady Moon, Nikhil Varma Keetha

This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
'''

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import ta_download  # noqa: E402

BUCKET = 'tartanaviation-audio'
SAMPLE = 'kbtp/2020/11/11-02-20_audio.zip'
# Daily archives: <location>/<year>/<month, not zero-padded>/<MM-DD-YY>_audio.zip
DAILY = re.compile(r'^(kbtp|kagc)/(\d{4})/(\d{1,2})/\d{2}-\d{2}-\d{2}_audio\.zip$')


def year_month(text):
    try:
        year, month = (int(x) for x in text.split('-'))
        assert 1 <= month <= 12
    except (ValueError, AssertionError):
        raise argparse.ArgumentTypeError(f'expected YYYY-MM, got {text!r}')
    return year, month


def main():
    parser = argparse.ArgumentParser(description='Download TartanAviation Audio Dataset')
    ta_download.add_common_args(parser)
    parser.add_argument('--option', type=str, required=True, choices=['Sample', 'All', 'Date_Range', 'Raw'],
                        help='Sample: one day at KBTP. All: every day. Date_Range: days between --start_date '
                             'and --end_date. Raw: unprocessed two-month recordings')
    parser.add_argument('--location', type=str, default='Both', choices=['kbtp', 'kagc', 'Both'], help='Data airport location')
    parser.add_argument('--start_date', type=year_month, default='2020-09', help='Start month, inclusive (YYYY-MM)')
    parser.add_argument('--end_date', type=year_month, default='2023-02', help='End month, inclusive (YYYY-MM)')
    args = parser.parse_args()

    locations = ['kbtp', 'kagc'] if args.location == 'Both' else [args.location]

    jobs = []
    if args.option == 'Raw':
        # Raw recordings are kept zipped: <save_dir>/Raw/<location>/<year>/<months>.zip
        for location in locations:
            for key, size in sorted(ta_download.list_objects(BUCKET, f'Raw/{location}/').items()):
                jobs.append(ta_download.Job(key, size, os.path.join(args.save_dir, key)))
    else:
        if args.option == 'Sample':
            keys = ta_download.list_objects(BUCKET, SAMPLE)
        else:
            keys = {}
            for location in locations:
                for key, size in ta_download.list_objects(BUCKET, f'{location}/').items():
                    match = DAILY.match(key)
                    if not match:
                        continue
                    month = (int(match.group(2)), int(match.group(3)))
                    if args.option == 'All' or args.start_date <= month <= args.end_date:
                        keys[key] = size
        # Each day is extracted into <save_dir>/<location>/<year>/<month>/<MM-DD-YY>_audio/
        for key, size in sorted(keys.items()):
            local = os.path.join(args.save_dir, key[:-len('.zip')])
            jobs.append(ta_download.Job(key, size, f'{local}.zip', extract_to=local, flatten=True))

    ta_download.run(BUCKET, jobs, args.save_dir, args.dry_run)


if __name__ == '__main__':
    main()
