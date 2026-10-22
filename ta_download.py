'''
Copyright (c) AirLab Stacks and Carnegie Mellon University.
All rights reserved.

Shared helpers for the TartanAviation download scripts. Standard library only.

The data is served from a public Ceph/Swift object store. Objects are fetched
with plain HTTPS GETs and buckets are listed with the Swift JSON listing API,
so no credentials or S3 client are needed.

This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
'''

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from typing import NamedTuple, Optional

BASE_URL = 'https://airlab-cloud.andrew.cmu.edu:8080/swift/v1/AUTH_ac8533a83cff4d48bc8c608ad222d330'
CHUNK = 1 << 20
RETRIES = 5


def object_url(bucket, key):
    return f'{BASE_URL}/{bucket}/{urllib.parse.quote(key)}'


def list_objects(bucket, prefix=''):
    '''Return {key: size_in_bytes} for every object in `bucket` under `prefix`.'''
    objects, marker = {}, ''
    while True:
        query = urllib.parse.urlencode({'format': 'json', 'prefix': prefix, 'marker': marker, 'limit': 10000})
        with urllib.request.urlopen(f'{BASE_URL}/{bucket}/?{query}', timeout=60) as resp:
            page = json.load(resp)
        if not page:
            return objects
        for obj in page:
            objects[obj['name']] = obj['bytes']
        marker = page[-1]['name']


def human(n):
    '''Format a byte count with decimal units, e.g. 733388340 -> "733.4 MB".'''
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1000:
            return f'{n:.0f} {unit}' if unit == 'B' else f'{n:.1f} {unit}'
        n /= 1000
    return f'{n:.2f} TB'


def _progress(name, done, total, start):
    rate = done / max(time.time() - start, 1e-6)
    pct = 100 * done / total if total else 100
    bar = '#' * int(pct / 4)
    sys.stdout.write(f'\r  {name}: [{bar:<25}] {pct:5.1f}%  {human(done)} / {human(total)}  {human(rate)}/s ')
    sys.stdout.flush()


def download(bucket, key, dest, size):
    '''Download one object to `dest`, resuming a partial `.part` file if present.'''
    os.makedirs(os.path.dirname(dest) or '.', exist_ok=True)
    part = dest + '.part'
    name = os.path.basename(dest)
    start = time.time()
    for attempt in range(1, RETRIES + 1):
        done = os.path.getsize(part) if os.path.exists(part) else 0
        if done > size:
            os.remove(part)
            done = 0
        try:
            if done < size:
                req = urllib.request.Request(object_url(bucket, key), headers={'Range': f'bytes={done}-'})
                with urllib.request.urlopen(req, timeout=60) as resp, open(part, 'ab' if done else 'wb') as f:
                    if done and resp.status != 206:  # server ignored the range: start over
                        f.truncate(0)
                        done = 0
                    while chunk := resp.read(CHUNK):
                        f.write(chunk)
                        done += len(chunk)
                        _progress(name, done, size, start)
            else:
                open(part, 'ab').close()
            print()
            os.replace(part, dest)
            return True
        except (urllib.error.URLError, OSError) as err:
            print(f'\n  {name}: attempt {attempt}/{RETRIES} failed ({err})')
            time.sleep(min(2 ** attempt, 30))
    print(f'  Giving up on {key}; rerun the script to resume.')
    return False


def extract(zip_path, out_dir, flatten=False):
    '''Extract `zip_path` into `out_dir` and delete the archive. Returns False if it could not.'''
    os.makedirs(out_dir, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path) as zf:
            if not flatten:
                zf.extractall(out_dir)
            else:  # like `unzip -j`: drop the directory structure inside the archive
                for info in zf.infolist():
                    if info.is_dir() or info.filename.startswith('__MACOSX/'):
                        continue
                    with zf.open(info) as src, open(os.path.join(out_dir, os.path.basename(info.filename)), 'wb') as dst:
                        shutil.copyfileobj(src, dst)
    except NotImplementedError:
        # Some archives use Deflate64, which Python's zipfile cannot read; Info-ZIP `unzip` can.
        if shutil.which('unzip') is None:
            print(f'  {os.path.basename(zip_path)} uses Deflate64, which needs `unzip` '
                  f'(e.g. sudo apt install unzip). The archive is kept; rerun once it is installed.')
            return False
        cmd = ['unzip', '-q', '-o'] + (['-j'] if flatten else []) + [zip_path, '-d', out_dir]
        if subprocess.run(cmd).returncode != 0:
            print(f'  unzip failed on {zip_path}; the archive is kept.')
            return False
    os.remove(zip_path)
    return True


class Job(NamedTuple):
    key: str                        # object key in the bucket
    size: int                       # bytes, from the bucket listing
    zip_path: str                   # where the archive is written
    extract_to: Optional[str] = None  # extract here and delete the archive; None keeps the archive
    flatten: bool = False           # drop the archive's internal folders when extracting

    def done(self):
        if self.extract_to is None:
            return os.path.exists(self.zip_path)
        # Extraction deletes the archive, so a leftover archive means it was interrupted.
        return (os.path.isdir(self.extract_to) and not os.path.exists(self.zip_path)
                and not os.path.exists(self.zip_path + '.part'))


def add_common_args(parser):
    parser.add_argument('--save_dir', type=str, default='./data', help='Directory to save the dataset')
    parser.add_argument('--dry_run', action='store_true', help='List what would be downloaded and its size, then exit')


def run(bucket, jobs, save_dir, dry_run=False):
    '''Download (and extract) every job not already on disk. Returns the jobs that completed.'''
    todo = [job for job in jobs if not job.done()]
    if len(todo) < len(jobs):
        print(f'{len(jobs) - len(todo)} file(s) already downloaded, skipping.')
    total = sum(job.size for job in todo)
    print(f'{len(todo)} file(s), {human(total)} to download into {os.path.abspath(save_dir)}')
    if dry_run:
        for job in todo:
            print(f'  {human(job.size):>10}  {job.key}')
        print('Dry run: nothing downloaded.')
        return []
    if not todo:
        return []
    os.makedirs(save_dir, exist_ok=True)
    free = shutil.disk_usage(save_dir).free
    if free < total:
        print(f'Warning: only {human(free)} free on that disk.')

    completed, failed = [], []
    for i, job in enumerate(todo, 1):
        print(f'[{i}/{len(todo)}] {job.key}')
        if not os.path.exists(job.zip_path) and not download(bucket, job.key, job.zip_path, job.size):
            failed.append(job.key)
            continue
        if job.extract_to is not None:
            try:
                extracted = extract(job.zip_path, job.extract_to, job.flatten)
            except zipfile.BadZipFile:
                os.remove(job.zip_path)
                print('  Corrupt archive, deleted; rerun to fetch it again.')
                extracted = False
            if not extracted:
                failed.append(job.key)
                continue
        completed.append(job)
    print(f'Done: {len(completed)} downloaded, {len(failed)} failed.')
    for key in failed:
        print(f'  failed: {key}')
    return completed
