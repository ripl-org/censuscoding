import hashlib
import json
from ftplib import FTP
import os
import censuscoding
import urllib.request

URLS = {}
state_codes = {}
urls_json_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), './urls.json')
state_codes_json_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), './state_codes.json')
file_hashes_json_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), './file_hashes.json')
downloads_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), './downloads')
info = censuscoding.Log(__name__, "download").info


def state_exists(state):  # we can separate the existence check functions for e911 and TIGER files
    return state in URLS


def calc_sha1(fp):
    sha1sum = hashlib.sha1()
    block = fp.read(2 ** 16)
    while len(block) != 0:
        sha1sum.update(block)
        block = fp.read(2 ** 16)

    return sha1sum.hexdigest()


def check_hash(file_name):
    file_path = os.path.join(downloads_path, file_name)
    try:
        with open(file_hashes_json_path) as json_file:  # read state codes (e.g "ri":"44") into state_codes
            file_hashes = json.load(json_file)
    except Exception as e:
        pass

    with open(file_path, 'rb') as fp:
        file_hash = calc_sha1(fp)

    if file_name in file_hashes and file_hashes[file_name] == file_hash:
        return True

    os.remove(file_path)
    info("File hashes does not match. File removed.")
    return False


class Downloader:

    def __init__(self, state):
        global URLS, urls_json_path, state_codes

        with open(urls_json_path, 'a'):  # creates the json file if it doesn't exist
            pass

        try:
            with open(urls_json_path) as json_file:  # read URLS json data into URLS
                URLS = json.load(json_file)
        except Exception as e:
            pass

        try:
            with open(state_codes_json_path) as json_file:  # read state codes (e.g "ri":"44") into state_codes
                state_codes = json.load(json_file)
        except Exception as e:
            pass

        self.state = state
        self.exists = state_exists(self.state)  # downloader object marks itself if it is already downloaded

    def download(self, update):
        global URLS

        if not os.path.exists(downloads_path):
            os.makedirs(downloads_path)

        # if file does not exist locally or user wants to update it, the if block gets executed
        if not self.exists or update:
            tiger_file_name = "tl_2020_" + state_codes[
                self.state.lower()] + "_bg.zip"  # for now only tiger archive is downloaded
            ftp = FTP('ftp2.census.gov')
            ftp.login()
            ftp.cwd('geo/tiger/TIGER2020/BG/')

            state_url_info = {}

            with open(os.path.join(downloads_path, tiger_file_name),
                      'wb') as fp:  # tiger file is downloaded into downloads directory
                ftp.retrbinary('RETR ' + tiger_file_name, fp.write)
            if check_hash(tiger_file_name):
                state_url_info["tiger_url"] = tiger_file_name
                info("Download completed: ", tiger_file_name)

            e911_file_name = "e911Sites21r1.zip"
            e911_url = "https://data.rigis.org/FACILITY/e911Sites21r1.zip"  # Hardcoded for now!
            urllib.request.urlretrieve(e911_url, os.path.join(downloads_path, e911_file_name))  # Hardcoded for now!

            if check_hash(e911_file_name):
                state_url_info["e911_url"] = e911_file_name
                info("Download completed: ", e911_file_name)

            URLS[self.state] = state_url_info

            with open(urls_json_path, 'w') as outfile:
                json.dump(URLS, outfile)


        else:
            info("State already exists")
