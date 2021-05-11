import hashlib
import os
import tempfile
from ftplib import FTP

import censuscoding
import json

info = censuscoding.Log(__name__, "download").info

state_codes = {}
url_hashes = {}
state_codes_json_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), './state_codes.json')
file_hashes_json_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), './file_hashes.json')


def calculate_and_store_checksums():  # downloads all TIGER files, calculates and stores sha1 checksum values into a file as json
    global state_codes

    try:
        with open(state_codes_json_path) as json_file:  # read state codes (e.g "ri":"44") into state_codes
            state_codes = json.load(json_file)
    except Exception as e:
        pass

    for k, v in state_codes.items():
        tiger_url = "tl_2020_" + v + "_bg.zip"  # for now only tiger archive is downloaded
        ftp = FTP('ftp2.census.gov')
        ftp.login()
        ftp.cwd('geo/tiger/TIGER2020/BG/')

        with tempfile.TemporaryFile() as fp:
            ftp.retrbinary('RETR ' + tiger_url, fp.write)
            url_hashes[tiger_url] = calc_sha1(fp)
            print(tiger_url, url_hashes[tiger_url])

    with open(file_hashes_json_path, 'w') as outfile:
        json.dump(url_hashes, outfile)


def calc_sha1(fp):
    fp.flush()
    fp.seek(0)
    sha1sum = hashlib.sha1()
    block = fp.read(2 ** 16)
    while len(block) != 0:
        sha1sum.update(block)
        block = fp.read(2 ** 16)

    return sha1sum.hexdigest()


calculate_and_store_checksums()