import argparse
import censuscoding
import logging
import sys

def main():
    parser = argparse.ArgumentParser(description=censuscoding.__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

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

    # Required arguments
    parser.add_argument("-i", "--input",
                        required=True,
                        help="input CSV file containing [record_id, zip_code, address]")
    parser.add_argument("-o", "--output",
                        required=True,
                        help="output CSV file containing [record_id, zip_code, blkgrp]")

    # Optional arguments
    parser.add_argument("--record_id",
                        default="record_id",
                        help="field name corresponding to the record ID [default: 'record_id']")
    parser.add_argument("--zip_code",
                        default="zip_code",
                        help="field name corresponding to the zip code [default: 'zip_code']")
    parser.add_argument("--address",
                        default="address",
                        help="field name corresponding to the street address with street name and number [default: 'address']")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    censuscoding.censuscode(
        args.input,
        args.output,
        record_id=args.record_id,
        zip_code=args.zip_code,
        address=args.address
    )

if __name__ == "__main__":
    sys.exit(main())
