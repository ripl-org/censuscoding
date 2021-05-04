import json
from ftplib import FTP
import os
import censuscoding

URLS = {}
state_codes = {}
urls_json_path = 'urls.json'
state_codes_json_path = 'state_codes.json'
info = censuscoding.Log(__name__, "download").info


def state_exists(state):
    if "E911_URLS" in URLS and "TIGER_URLS" in URLS:
        return state in URLS["E911_URLS"] and state in URLS["TIGER_URLS"]
    return False


class Downloader:
    download_path = "downloads/"  # moving to another directory would be better (home etc.)

    def __init__(self, state):
        global URLS, urls_json_path, state_codes

        with open(urls_json_path, 'a'):
            pass

        try:
            with open(urls_json_path) as json_file:
                URLS = json.load(json_file)
        except Exception as e:
            pass

        try:
            with open(state_codes_json_path) as json_file:
                state_codes = json.load(json_file)
        except Exception as e:
            pass

        self.state = state
        self.exists = state_exists(self.state)

    def download(self, update):
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

        if not self.exists or update:
            tiger_url = "tl_2020_" + state_codes[self.state.lower()] + "_bg.zip"
            ftp = FTP('ftp2.census.gov')
            ftp.login()
            ftp.cwd('geo/tiger/TIGER2020/BG/')

            with open("downloads/" + tiger_url, 'wb') as fp:
                ftp.retrbinary('RETR ' + tiger_url, fp.write)

            if "TIGER_URLS" not in URLS:
                URLS["TIGER_URLS"] = {}

            if "E911_URLS" not in URLS:
                URLS["E911_URLS"] = {}

            URLS["TIGER_URLS"][self.state] = tiger_url
            URLS["E911_URLS"][self.state] = tiger_url  # temporary

            with open(urls_json_path, 'w') as outfile:
                json.dump(URLS, outfile)

            info("downloaded " + tiger_url)
        else:
            info("already exists")
