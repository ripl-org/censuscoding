import argparse
import censuscoding
import logging
import pandas as pd
import sys
from censuscoding.download import Downloader

def main():
    parser = argparse.ArgumentParser(description=censuscoding.__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(dest='command')
    download = subparsers.add_parser('download', help='The download will automatically download these files for you and store them in the censuscoding package')
    code = subparsers.add_parser('code', help='Censuscoding uses publicly available E911 data to map addresses to lat/lon coordinates. ')

    # Basic arguments
    parser.add_argument("-v", "--version",
                        action="version",
                        version="censuscoding {}".format(censuscoding.__version__))
    parser.add_argument("-q", "--quiet",
                        action="store_true",
                        help="suppress all logging messages except for errors")
    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="show all logging messages, including debugging output")


    # download Required arguments
    download.add_argument('-s','--state', required=True, help='state name to download')

    # download Optional arguments
    download.add_argument("--update",
                        action='store_true',
                        help="field to force redownload already downloaded files")

    # code Required arguments
    code.add_argument("-i", "--input",
                        required=True,
                        help="input CSV file containing [record_id, zip_code, street, street_num]")
    code.add_argument("-o", "--output",
                        required=True,
                        help="output CSV file containing [record_id, zip_code, blkgrp]")
    code.add_argument("--lookup_streets",
                        required=True,
                        help="input CSV file containing the street-level lookup table")
    code.add_argument("--lookup_nums",
                        required=True,
                        help="input CSV file containing the street-number-level lookup table")

    # code Optional arguments
    code.add_argument("--record_id",
                        default="record_id",
                        help="field name corresponding to the record ID [default: 'record_id']")
    code.add_argument("--zip_code",
                        default="zip_code",
                        help="field name corresponding to the zip code [default: 'zip_code']")
    code.add_argument("--address",
                        default="address",
                        help="field name corresponding to the street address with street name and number [default: 'address']")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.command == 'download':
        downloader = Downloader(args.state)
        downloader.download(args.update)

    elif args.command == 'code':
        info = censuscoding.Log(__name__, "main").info
        info("Loading lookup files")
        lookup_streets = pd.read_csv(args.lookup_streets, low_memory=False)
        lookup_nums = pd.read_csv(args.lookup_nums, low_memory=False)

        censuscoding.censuscode(
            args.input,
            args.output,
            lookup_streets,
            lookup_nums,
            record_id=args.record_id,
            zip_code=args.zip_code,
            address=args.address
        )



if __name__ == "__main__":
    sys.exit(main())
